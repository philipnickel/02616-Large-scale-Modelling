import numpy as np
from time import perf_counter as time
from mpi4py import MPI

# Get current rank
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# Get size
size = comm.Get_size()

N = 32

def distribute_size(arr):
    """ Just to allocate the correct buffer on the receiving end.

    We could just as well return the maximum size
    """
    size = 0
    if rank == 0:
        size = int(arr.size)
    size = comm.bcast(size, root=0)
    return size

# a)
def distribute_sr(arr):
    # distribute the size of the arrays
    n = distribute_size(arr)
    t0 = time()
    if rank == 0:
        reqs = []
        for dest in range(1, size):
            reqs.append(comm.Isend(arr, dest=dest, tag=dest))
        MPI.Request.waitall(reqs)
    else:
        buf = np.empty(n)
        comm.Recv(buf, source=0, tag=rank)
    return time() - t0

# b)
def distribute_bcast(arr):
    # distribute the size of the arrays
    n = distribute_size(arr)
    t0 = time()
    if rank == 0:
        comm.Bcast(arr, root=0)
    else:
        buf = np.empty(n)
        comm.Bcast(buf, root=0)
    return time() - t0


# Do experiments
arr = None
mb = []
s_sr = []
s_bcast = []
for kb in np.logspace(0, 6, num=N):
    # elements
    mb.append(kb / 1024)
    n = int(kb * 1024 / 8)
    if rank == 0:
        # only allocate on the first rank
        arr = np.zeros(n)
    else:
        arr = None
    s_sr.append(distribute_sr(arr))
    s_bcast.append(distribute_bcast(arr))

mb = np.asarray(mb)

# plot the data (for all ranks)
from matplotlib import pyplot as plt
label = {0: "Isend"}.get(rank, "Recv")
plt.plot(mb, mb / s_sr, label=label)
plt.plot(mb, mb / s_bcast, label="Bcast")
plt.loglog()
plt.xlabel("Array size in MB")
plt.legend()
plt.ylabel(f"Bandwidth ({rank=}) MB/s")
plt.show()
