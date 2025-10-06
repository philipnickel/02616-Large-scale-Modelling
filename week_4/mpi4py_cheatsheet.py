from mpi4py import MPI
import numpy as np

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

assert size >= 2, "Too few ranks in MPI for this cheatsheet"

def free(req):
    try:
        req.free()
    except: pass

# -----------------------------
# Point-to-Point Communication
# -----------------------------

# Blocking Send/Recv
if rank == 0:
    data = np.array([42], dtype=np.int32)
    comm.Send([data, MPI.INT], dest=1, tag=0)
    print(f"Rank {rank} sent {data[0]}")
elif rank == 1:
    recv_buf = np.empty(1, dtype=np.int32)
    comm.Recv([recv_buf, MPI.INT], source=0, tag=0)
    print(f"Rank {rank} received {recv_buf[0]}")

# Non-blocking Isend/Irecv
if rank == 0:
    data = np.array([99], dtype=np.int32)
    req = comm.Isend([data, MPI.INT], dest=1, tag=1)
    req.Wait()  # Ensure completion
    free(req)
    print(f"Rank {rank} non-blocking sent {data[0]}")
elif rank == 1:
    recv_buf = np.empty(1, dtype=np.int32)
    req = comm.Irecv([recv_buf, MPI.INT], source=0, tag=1)
    # Another way to call Wait
    MPI.Request.Wait(req)  # Ensure completion
    free(req)
    print(f"Rank {rank} non-blocking received {recv_buf[0]}")


# -----------------------------
# Collectives (blocking)
# -----------------------------

# Broadcast (root=0)
if rank == 0:
    data = np.array([rank], dtype=np.int32)
else:
    data = np.empty(1, dtype=np.int32)
comm.Bcast([data, MPI.INT], root=0)
print(f"Rank {rank} after Bcast has {data[0]}")

# Scatter (root=0)
if rank == 0:
    send_buf = np.arange(size, dtype=np.int32)
else:
    send_buf = None
recv_buf = np.empty(1, dtype=np.int32)
comm.Scatter([send_buf, MPI.INT], [recv_buf, MPI.INT], root=0)
print(f"Rank {rank} received {recv_buf[0]} from Scatter")

# Gather (root=0)
send_buf = np.array([rank], dtype=np.int32)
if rank == 0:
    recv_buf = np.empty(size, dtype=np.int32)
else:
    recv_buf = None
comm.Gather([send_buf, MPI.INT], [recv_buf, MPI.INT], root=0)
if rank == 0:
    print(f"Rank {rank} gathered {recv_buf}")

# Reduce (sum, root=0)
send_buf = np.array([rank], dtype=np.int32)
if rank == 0:
    recv_buf = np.empty(1, dtype=np.int32)
else:
    recv_buf = None
comm.Reduce([send_buf, MPI.INT], [recv_buf, MPI.INT], op=MPI.SUM, root=0)
if rank == 0:
    print(f"Rank {rank} reduced sum = {recv_buf[0]}")


# -------------------------------
# Global collectives (blocking)
# -------------------------------

# Alltoall (scatter merged with a gather)
send_buf = np.full(size, rank, dtype=np.int32)
recv_buf = np.empty(size, dtype=np.int32)
# The count is the *number of elements sent to the other processors*
# It will internally automatically divide by the *size* of the communicator.
# But raise an error if the size is not divisible.
comm.Alltoall([send_buf, MPI.INT], [recv_buf, 1, MPI.INT])
print(f"Rank {rank} all-to-all {recv_buf}")

# Allgather
send_buf = np.array([rank], dtype=np.int32)
recv_buf = np.empty(size, dtype=np.int32)
comm.Allgather([send_buf, MPI.INT], [recv_buf, MPI.INT])
print(f"Rank {rank} all-gathered {recv_buf}")

# AllReduce (sum, root=0)
send_buf = np.array([rank], dtype=np.int32)
recv_buf = np.empty(1, dtype=np.int32)
comm.Allreduce([send_buf, MPI.INT], [recv_buf, MPI.INT], op=MPI.SUM)
print(f"Rank {rank} all-reduced sum = {recv_buf[0]}")
