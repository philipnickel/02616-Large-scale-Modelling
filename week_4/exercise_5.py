#!/usr/bin/env python3
"""
Exercise 5: Reduce operation
All ranks contribute values that are reduced (summed) to a single value on rank 0.
For Python objects, use a custom callable. For numpy arrays, use MPI operators.
"""

from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Rank {rank} of {size} processes starting reduce operation")

# Example 1: Reducing Python objects (integers) with custom callable
print("=== Python object reduction ===")
local_value = rank * rank  # Each rank contributes its rank squared

# Reduce to rank 0 using custom lambda function
reduced_sum = comm.reduce(local_value, op=lambda a, b: a + b, root=0)

if rank == 0:
    expected_sum = sum(i * i for i in range(size))
    print(f"Rank {rank}: Reduced sum of squares: {reduced_sum}")
    print(f"Rank {rank}: Expected sum: {expected_sum}")
    print(f"Rank {rank}: Verification: {'PASS' if reduced_sum == expected_sum else 'FAIL'}")
else:
    print(f"Rank {rank}: Contributed value {local_value} to reduction")

# Example 2: Reducing numpy arrays with MPI operators
print("=== Numpy array reduction ===")
array_size = 100
local_array = np.full(array_size, rank + 1, dtype=np.float64)  # Array filled with (rank+1)

if rank == 0:
    # Root process needs to allocate space for the result
    global_sum = np.empty(array_size, dtype=np.float64)
else:
    global_sum = None

# Reduce arrays using MPI.SUM
comm.Reduce(local_array, global_sum, op=MPI.SUM, root=0)

if rank == 0:
    expected_value = sum(range(1, size + 1))  # Sum of (1+2+...+size)
    print(f"Rank {rank}: First 5 elements of reduced array: {global_sum[:5]}")
    print(f"Rank {rank}: Expected value per element: {expected_value}")
    print(f"Rank {rank}: Verification: {'PASS' if np.allclose(global_sum, expected_value) else 'FAIL'}")
else:
    print(f"Rank {rank}: Contributed array with value {rank + 1} per element")

# Example 3: Different reduction operations
print("=== Different reduction operations ===")
local_number = rank + 1  # Values 1, 2, 3, ..., size

if rank == 0:
    # Prepare result variables
    max_result = np.array(0, dtype=np.int32)
    min_result = np.array(0, dtype=np.int32)
    prod_result = np.array(0, dtype=np.int32)
else:
    max_result = None
    min_result = None
    prod_result = None

# Convert to numpy array for MPI operations
local_array_int = np.array(local_number, dtype=np.int32)

# Find maximum
comm.Reduce(local_array_int, max_result, op=MPI.MAX, root=0)
# Find minimum
comm.Reduce(local_array_int, min_result, op=MPI.MIN, root=0)
# Calculate product
comm.Reduce(local_array_int, prod_result, op=MPI.PROD, root=0)

if rank == 0:
    print(f"Rank {rank}: Maximum value: {max_result.item()} (expected: {size})")
    print(f"Rank {rank}: Minimum value: {min_result.item()} (expected: 1)")
    factorial = 1
    for i in range(1, size + 1):
        factorial *= i
    print(f"Rank {rank}: Product: {prod_result.item()} (expected: {factorial})")
else:
    print(f"Rank {rank}: Contributed value {local_number} to min/max/product reductions")

print(f"Rank {rank}: Reduce operations completed")