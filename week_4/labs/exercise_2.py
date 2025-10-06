#!/usr/bin/env python3
"""
Exercise 2: Ring communication
Every rank sends information to rank+1, except the last rank which sends to rank 0.
Rank 0 starts by sending data around the ring.
"""

from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Rank {rank} of {size} processes starting ring communication")

# Data to send around the ring
data = np.array([rank * 10], dtype=np.int64)
received_data = np.empty(1, dtype=np.int64)

if rank == 0:
    # Rank 0 starts the ring by sending to rank 1
    next_rank = (rank + 1) % size
    prev_rank = (rank - 1) % size

    print(f"Rank {rank}: Starting ring with data {data[0]}")
    comm.Send(data, dest=next_rank, tag=0)

    # Rank 0 receives the data after it has traveled around the ring
    comm.Recv(received_data, source=prev_rank, tag=0)
    print(f"Rank {rank}: Received data {received_data[0]} completing the ring")

else:
    # All other ranks receive from previous rank and send to next rank
    next_rank = (rank + 1) % size
    prev_rank = (rank - 1) % size

    # Receive from previous rank
    comm.Recv(received_data, source=prev_rank, tag=0)
    print(f"Rank {rank}: Received data {received_data[0]} from rank {prev_rank}")

    # Add our contribution to the data
    modified_data = received_data[0] + data[0]
    send_data = np.array([modified_data], dtype=np.int64)

    # Send to next rank
    comm.Send(send_data, dest=next_rank, tag=0)
    print(f"Rank {rank}: Sent modified data {send_data[0]} to rank {next_rank}")

print(f"Rank {rank}: Ring communication completed")
