import sys
import numpy as np
from mpi4py import MPI


# Good practice to copy COMM_WORLD! ;)
comm = MPI.COMM_WORLD.Clone()

"""
We will create some data-types that hosts some coordinates.
In this case each *element* of the data-type hosts 3 consecutive
values (Cartesian coordinates).
"""

DOUBLE_xyz = MPI.DOUBLE.Create_contiguous(3)
# Have to commit it!
DOUBLE_xyz.Commit()

# Ensure the extend (size of the data-type) matches 3 doubles!
lb, extend = DOUBLE_xyz.Get_extent()
assert lb == 0, "Expects the start of the memory at 0"
assert extend == 24, "Expects an extend of the data-type of 3*8=24 bytes"

# C-style arrays has the last axis as the memory
# consecutive layout.
xyz = np.zeros([60, 3], dtype=np.float64)

rank = comm.Get_rank()
xyz[...] = rank


def print_count(prefix: str, status: MPI.Status):
    counts = map(lambda dtype: status.Get_count(dtype),
                 [MPI.DOUBLE, DOUBLE_xyz])
    print(f"{prefix} [MPI.DOUBLE, DOUBLE_xyz]")
    print(" " * len(prefix) + " Get_count ", *counts)
    counts = map(lambda dtype: status.Get_elements(dtype),
                 [MPI.DOUBLE, DOUBLE_xyz])
    print(" " * len(prefix) + " Get_elements", *counts)


# receive to 0
if rank == 0:
    status = MPI.Status()

    comm.Recv(xyz, 1, tag=1, status=status)
    print_count("[tag=1]", status)
    assert np.allclose(xyz, 1)
    # reset data to check that we get the correct results
    xyz[...] = rank

    comm.Recv(xyz, 1, tag=2, status=status)
    print_count("[tag=2]", status)
    assert np.allclose(xyz, 1)
    # reset
    xyz[...] = rank

    comm.Recv([xyz, len(xyz), DOUBLE_xyz], 1, tag=3, status=status)
    print_count("[tag=3]", status)
    assert np.allclose(xyz, 1)
    xyz[...] = rank

elif rank == 1:
    comm.Send(xyz, 0, tag=1)

    # We'll send the full array again, note the length!
    # Why?
    comm.Send((xyz, len(xyz), DOUBLE_xyz), 0, tag=2)
    comm.Send((xyz, len(xyz), DOUBLE_xyz), 0, tag=3)
