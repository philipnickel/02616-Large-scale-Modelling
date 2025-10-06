"""
Exercise 3b: Collective gather operation
"""

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

send_data= rank * 10

# Gather all data to rank 0
gathered_data = comm.gather(send_data, root=0)

if rank == 0:
    print(f"Rank {rank}: Gathered values : {gathered_data}")
else:
    print(f"Rank {rank}: Sent value {send_data} via gather operation")
