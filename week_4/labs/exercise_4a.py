from mpi4py import MPI
import numpy as np
import time

"""
Exercise 4a: Manual Isend/Recv broadcasting with specific tags
Rank 0 distributes a numpy array to all other ranks 
"""

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Size of the array to broadcast
array_size = 1000
data_to_broadcast = np.arange(array_size, dtype=np.float64)

print(f"Rank {rank} of {size} processes starting")

if rank == 0:
    start_time = time.time()

    # Fill the array with data
    data_to_broadcast *= 10

    reqs = []
    for dest_rank in range(1, size):
        # Use rank-specific tags
        tag = dest_rank
        req = comm.Isend(data_to_broadcast, dest=dest_rank, tag=tag)
        reqs.append(req)
        print(f"Rank {rank}: Initiated send to rank {dest_rank} with tag {tag}")

    # Wait for all sends to complete
    MPI.Request.waitall(reqs)

    # Free the requests
    for req in reqs:
        req.free()

    end_time = time.time()
    bandwidth = (array_size * 8 * (size - 1)) / (end_time - start_time) / 1e6  # MB/s
    print(f"Rank {rank}: Manual broadcast completed in {end_time - start_time:.6f}s")
    print(f"Rank {rank}: Bandwidth: {bandwidth:.2f} MB/s")

else:
    # All other ranks receive the array from rank 0
    start_time = time.time()

    received_data = np.empty(array_size, dtype=np.float64)
    tag = rank  # Use own rank as tag

    comm.Recv(received_data, source=0, tag=tag)

    end_time = time.time()
    print(f"Rank {rank}: Received array (first 5 elements: {received_data[:5]}) in {end_time - start_time:.6f}s")


