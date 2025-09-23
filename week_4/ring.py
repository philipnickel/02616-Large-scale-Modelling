# ring.py
from mpi4py import MPI

comm  = MPI.COMM_WORLD
rank  = comm.Get_rank()
size  = comm.Get_size()

TAG   = 1
right = (rank + 1) % size
left  = (rank - 1) % size
print(f"right: {right}, left: {left}")

if size < 2:
    if rank == 0:
        print("Ring needs at least 2 ranks.")
    raise SystemExit

if rank == 0:
    print(f"Rank {rank}: Starting ring")
    msg = "Hello from rank 0"
    comm.send(msg, dest=right, tag=TAG)

    # Receive the final message back from the last rank
    data = comm.recv(source=left, tag=TAG)
    print(f"Rank {rank}: Received back: {data}")

else:
    # Receive from left neighbor
    data = comm.recv(source=left, tag=TAG)

    # Append this rank to the chain
    new_data = f"{data} -> rank {rank}"

    # Print the forward trace
    print(f"Rank {rank}: Forwarded: {new_data}")

    # Send to right neighbor (wraps to 0 for the last rank)
    comm.send(new_data, dest=right, tag=TAG)
