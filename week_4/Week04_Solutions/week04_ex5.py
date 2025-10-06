from time import perf_counter as time
from mpi4py import MPI

# Get current rank
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# Get size
size = comm.Get_size()

# a)
def reduce_sr(value):
    t0 = time()
    if rank == 0:
        ret = value
        for source in range(1, size):
            ret += comm.recv(source=source)
        print(ret)
    else:
        comm.send(value, dest=0)
    return time() - t0

# b)
def reduce_bcast(value):
    t0 = time()
    ret = comm.reduce(value, op=lambda a, b: a + b, root=0)
    if rank == 0:
        print(ret)
    return time() - t0


print(rank, reduce_sr(rank + 2))
print(rank, reduce_bcast(rank + 2))
