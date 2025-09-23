"""
Exercise 3a: Manual send/recv gathering
Rank 0 receives values from all other ranks 
stores them in a list, and prints the final list.
"""

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Rank 0 receives values from all other ranks
    gathered_values = [rank]  # Init with own 

    for source_rank in range(1, size):
        data = comm.recv(source=source_rank, tag=0)
        gathered_values.append(data)

    print(f"Rank {rank}: Gathered values: {gathered_values}")
else:
    # All other ranks send to rank 0
    send_data = rank * 10
    comm.send(send_data, dest=0, tag=0)
    print(f"Rank {rank}: Sent value {send_data} to rank 0")
