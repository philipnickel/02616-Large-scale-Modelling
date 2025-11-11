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

# Approach 1: Create data-type for ONE coordinate (x,y) and send multiple
# Create data-type for x, y components only (2 consecutive doubles)
# First create the basic type
DOUBLE_xy_base = MPI.DOUBLE.Create_contiguous(2)
# Resize to have extent of 24 bytes (3 doubles) to match array row size
DOUBLE_xy = DOUBLE_xy_base.Create_resized(0, 24)
DOUBLE_xy.Commit()
DOUBLE_xy_base.Free()

lb_xy, extend_xy = DOUBLE_xy.Get_extent()
assert lb_xy == 0, "Expects the start of the memory at 0"
assert extend_xy == 24, "Extent must match row size (3*8=24 bytes)"

# Approach 2: Create data-type for ALL coordinates using Create_vector
# This describes the entire pattern: 60 blocks of 2 doubles, stride of 3 doubles
DOUBLE_xy_vector = MPI.DOUBLE.Create_vector(
    count=60,        # 60 coordinates
    blocklength=2,   # each has 2 doubles (x,y)
    stride=3         # spaced 3 doubles apart in memory
)
DOUBLE_xy_vector.Commit()

# Create data-type for x, z components (skip y component)
# Approach 1: One coordinate at a time
DOUBLE_xz_base = MPI.DOUBLE.Create_indexed([1, 1], [0, 2])
# Resize to have extent of 24 bytes (3 doubles) to match array row size
DOUBLE_xz = DOUBLE_xz_base.Create_resized(0, 24)
DOUBLE_xz.Commit()
DOUBLE_xz_base.Free()

lb_xz, extend_xz = DOUBLE_xz.Get_extent()
assert lb_xz == 0, "Expects the start of the memory at 0"
assert extend_xz == 24, "Extent must match row size (3*8=24 bytes)"

# Approach 2: All coordinates using Create_indexed_block
# For x,z we need to pick elements at positions: 0,2, 3,5, 6,8, ... (x,z from each row)
# We can use Create_vector with a custom base type
DOUBLE_xz_one = MPI.DOUBLE.Create_indexed([1, 1], [0, 2])  # x and z from one row
DOUBLE_xz_one_resized = DOUBLE_xz_one.Create_resized(0, 24)  # stride to next row
DOUBLE_xz_vector = DOUBLE_xz_one_resized.Create_contiguous(60)  # 60 rows
DOUBLE_xz_vector.Commit()
DOUBLE_xz_one.Free()
DOUBLE_xz_one_resized.Free()

# C-style arrays has the last axis as the memory
# consecutive layout.
xyz = np.zeros([60, 3], dtype=np.float64)

rank = comm.Get_rank()
xyz[...] = rank


def print_count(prefix: str, status: MPI.Status):
    counts = map(lambda dtype: status.Get_count(dtype),
                 [MPI.DOUBLE, DOUBLE_xyz, DOUBLE_xy, DOUBLE_xz])
    print(f"{prefix} [MPI.DOUBLE, DOUBLE_xyz, DOUBLE_xy, DOUBLE_xz]")
    print(" " * len(prefix) + " Get_count ", *counts)
    counts = map(lambda dtype: status.Get_elements(dtype),
                 [MPI.DOUBLE, DOUBLE_xyz, DOUBLE_xy, DOUBLE_xz])
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

    # Test x,y components only (DOUBLE_xy)
    comm.Recv([xyz, len(xyz), DOUBLE_xy], 1, tag=4, status=status)
    print_count("[tag=4]", status)
    # Only x,y components should be received (columns 0,1)
    assert np.allclose(xyz[:, :2], 1), "x,y components should be 1"
    assert np.allclose(xyz[:, 2], 0), "z component should remain 0"
    xyz[...] = rank

    # Test x,z components only (DOUBLE_xz)
    comm.Recv([xyz, len(xyz), DOUBLE_xz], 1, tag=5, status=status)
    print_count("[tag=5]", status)
    # Only x,z components should be received (columns 0,2)
    assert np.allclose(xyz[:, 0], 1), "x component should be 1"
    assert np.allclose(xyz[:, 1], 0), "y component should remain 0"
    assert np.allclose(xyz[:, 2], 1), "z component should be 1"
    xyz[...] = rank

elif rank == 1:
    comm.Send(xyz, 0, tag=1)

    # We'll send the full array again, note the length!
    # Why?
    comm.Send((xyz, len(xyz), DOUBLE_xyz), 0, tag=2)
    comm.Send((xyz, len(xyz), DOUBLE_xyz), 0, tag=3)

    # Send only x,y components
    comm.Send((xyz, len(xyz), DOUBLE_xy), 0, tag=4)

    # Send only x,z components
    comm.Send((xyz, len(xyz), DOUBLE_xz), 0, tag=5)

# Free the created data-types
DOUBLE_xyz.Free()
DOUBLE_xy.Free()
DOUBLE_xz.Free()
