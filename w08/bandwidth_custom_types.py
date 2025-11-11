#!/usr/bin/env python3
"""
Week 8 – custom MPI datatypes bandwidth comparison.

We benchmark three ways of sending only two components (x,y or x,z) from an
array that stores Cartesian coordinates as [x, y, z]:

1. Copy the x and z components into a contiguous temporary buffer before
   sending (baseline).
2. Use a custom datatype for (x, z) built with `Create_indexed` +
   `Create_resized`.
3. Use a custom datatype for (x, y) built with `Create_struct` +
   `Create_resized`.

For each method we reuse the week 4 ping-pong bandwidth measurement and
generate a single plot comparing the achieved bandwidth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from mpi4py import MPI

# -----------------------------------------------------------------------------
# MPI setup and constants
# -----------------------------------------------------------------------------

comm = MPI.COMM_WORLD.Clone()
rank = comm.Get_rank()
size = comm.Get_size()

if size != 2:
    raise RuntimeError(
        "This benchmark requires exactly 2 MPI processes. "
        "Run with e.g. `mpirun -np 2 python bandwidth_custom_types.py`."
    )

PARTNER = 1 - rank
FLOAT_ITEMSIZE = MPI.DOUBLE.Get_size()  # 8 bytes for float64
ROW_EXTENT = 3 * FLOAT_ITEMSIZE        # sizeof([x, y, z])
SENTINEL = -12345.6789

# We measure message sizes identical to week 4 (2^10 .. 2^24 bytes)
MIN_POWER = 10
MAX_POWER = 24
MESSAGE_BYTES = [2 ** p for p in range(MIN_POWER, MAX_POWER + 1)]
BYTES_PER_ROW = 2 * FLOAT_ITEMSIZE  # sending two components (x?, y/z)
ROW_COUNTS = [max(1, msg // BYTES_PER_ROW) for msg in MESSAGE_BYTES]
MAX_ROWS = max(ROW_COUNTS)

NUM_REPETITIONS = 10


# -----------------------------------------------------------------------------
# Helper datatypes
# -----------------------------------------------------------------------------

def create_datatype_xz_indexed() -> MPI.Datatype:
    """Datatype that selects x and z from a single row via Create_indexed."""
    blocklengths = [1, 1]
    displacements = [0, 2]  # offsets counted in multiples of oldtype extent
    dtype = MPI.DOUBLE.Create_indexed(blocklengths, displacements)
    resized = dtype.Create_resized(0, ROW_EXTENT)
    dtype.Free()
    resized.Commit()
    return resized


def create_datatype_xy_struct() -> MPI.Datatype:
    """Datatype that selects x and y from a single row via Create_struct."""
    blocklengths = [1, 1]
    displacements = [0, FLOAT_ITEMSIZE]  # bytes
    oldtypes = [MPI.DOUBLE, MPI.DOUBLE]
    dtype = MPI.Datatype.Create_struct(blocklengths, displacements, oldtypes)
    resized = dtype.Create_resized(0, ROW_EXTENT)
    dtype.Free()
    resized.Commit()
    return resized


XZ_INDEXED = create_datatype_xz_indexed()
XY_STRUCT = create_datatype_xy_struct()


# -----------------------------------------------------------------------------
# Buffers
# -----------------------------------------------------------------------------

# Full coordinate arrays
send_xyz = np.empty((MAX_ROWS, 3), dtype=np.float64)
recv_xyz = np.empty((MAX_ROWS, 3), dtype=np.float64)

# Temporary buffers for the copy baseline
pack_buffer = np.empty((MAX_ROWS, 2), dtype=np.float64)
unpack_buffer = np.empty((MAX_ROWS, 2), dtype=np.float64)


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def component_pattern(for_rank: int) -> np.ndarray:
    """Return deterministic component values for verification."""
    base = 100.0 * for_rank
    return np.array([base + 1.0, base + 2.0, base + 3.0], dtype=np.float64)


def initialise_buffers(rows: int) -> None:
    """Seed send/receive buffers with predictable data and sentinels."""
    send_xyz[:rows, :] = component_pattern(rank)
    recv_xyz[:rows, :] = SENTINEL


def verify_receive(rows: int, case_key: str) -> None:
    """Assert that the receive buffer contains the expected pattern."""
    expected = component_pattern(PARTNER)

    if case_key in {"xz_copy", "xz_indexed"}:
        assert np.allclose(recv_xyz[:rows, 0], expected[0])
        assert np.allclose(recv_xyz[:rows, 2], expected[2])
        assert np.allclose(recv_xyz[:rows, 1], SENTINEL)
    elif case_key == "xy_struct":
        assert np.allclose(recv_xyz[:rows, 0], expected[0])
        assert np.allclose(recv_xyz[:rows, 1], expected[1])
        assert np.allclose(recv_xyz[:rows, 2], SENTINEL)
    else:
        raise ValueError(f"Unknown case key: {case_key}")


def check_sentinels(rows: int, untouched_index: int) -> None:
    """Confirm that untouched component stayed as the sentinel value."""
    assert np.allclose(recv_xyz[:rows, untouched_index], SENTINEL)


# -----------------------------------------------------------------------------
# Transfer primitives
# -----------------------------------------------------------------------------

def sendrecv_copy_xz(rows: int, tag: int) -> None:
    """Exchange x and z components using temporary copies."""
    np.copyto(pack_buffer[:rows], send_xyz[:rows, (0, 2)])
    comm.Sendrecv(
        sendbuf=pack_buffer[:rows],
        dest=PARTNER,
        sendtag=tag,
        recvbuf=unpack_buffer[:rows],
        source=PARTNER,
        recvtag=tag,
    )
    recv_xyz[:rows, (0, 2)] = unpack_buffer[:rows]


def sendrecv_datatype(rows: int, dtype: MPI.Datatype, tag: int) -> None:
    """Exchange components directly with a committed MPI datatype."""
    comm.Sendrecv(
        sendbuf=(send_xyz, rows, dtype),
        dest=PARTNER,
        sendtag=tag,
        recvbuf=(recv_xyz, rows, dtype),
        source=PARTNER,
        recvtag=tag,
    )


# -----------------------------------------------------------------------------
# Bandwidth measurement
# -----------------------------------------------------------------------------

@dataclass
class Case:
    key: str
    label: str
    untouched_component: int
    run_once: Callable[[int, int], None]
    base_tag: int


CASES: List[Case] = [
    Case(
        key="xz_copy",
        label="Copy buffer (x,z)",
        untouched_component=1,
        run_once=sendrecv_copy_xz,
        base_tag=110,
    ),
    Case(
        key="xz_indexed",
        label="Datatype indexed (x,z)",
        untouched_component=1,
        run_once=lambda rows, tag: sendrecv_datatype(rows, XZ_INDEXED, tag),
        base_tag=210,
    ),
    Case(
        key="xy_struct",
        label="Datatype struct (x,y)",
        untouched_component=2,
        run_once=lambda rows, tag: sendrecv_datatype(rows, XY_STRUCT, tag),
        base_tag=310,
    ),
]


def verify_case(rows: int, case: Case, tag: int) -> None:
    """Perform one verified exchange before timing."""
    initialise_buffers(rows)
    case.run_once(rows, tag)
    verify_receive(rows, case.key)
    check_sentinels(rows, case.untouched_component)


def measure_case(rows: int, case: Case, msg_index: int) -> float:
    """Return average round-trip time for a given case and number of rows."""
    total = 0.0
    for rep in range(NUM_REPETITIONS):
        initialise_buffers(rows)
        tag = case.base_tag + msg_index * 32 + rep
        comm.Barrier()
        start = MPI.Wtime()
        case.run_once(rows, tag)
        end = MPI.Wtime()
        total += end - start

        # Cheap validation to ensure untouched component stayed untouched
        check_sentinels(rows, case.untouched_component)

    return total / NUM_REPETITIONS


def gather_bandwidths() -> Dict[str, Tuple[List[float], List[float]]]:
    """Compute bandwidth curves for each case."""
    results: Dict[str, Tuple[List[float], List[float]]] = {}

    for msg_index, (msg_bytes, rows) in enumerate(zip(MESSAGE_BYTES, ROW_COUNTS)):
        for case in CASES:
            verify_case(rows, case, case.base_tag + msg_index * 32 - 1)
            avg_time = measure_case(rows, case, msg_index)

            if rank == 0:
                bandwidth_mb_s = (2 * msg_bytes) / avg_time / (1024 * 1024)
                payload_mb = msg_bytes / (1024 * 1024)

                payloads, bandwidths = results.setdefault(case.key, ([], []))
                payloads.append(payload_mb)
                bandwidths.append(bandwidth_mb_s)

    return results


# -----------------------------------------------------------------------------
# Driver
# -----------------------------------------------------------------------------

def main() -> None:
    results = gather_bandwidths()

    if rank == 0:
        plt.figure(figsize=(10, 6))
        for case in CASES:
            payloads, bandwidths = results[case.key]
            plt.loglog(payloads, bandwidths, marker="o", linewidth=2, label=case.label)

        plt.xlabel("Payload size (MB)")
        plt.ylabel("Bandwidth (MB/s)")
        plt.title("Bandwidth comparison: copy vs. custom MPI datatypes")
        plt.grid(True, which="both", linestyle="--", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig("bandwidth_custom_types.png", dpi=300)
        print("Saved plot -> bandwidth_custom_types.png")


if __name__ == "__main__":
    try:
        main()
    finally:
        XZ_INDEXED.Free()
        XY_STRUCT.Free()
        comm.Free()
