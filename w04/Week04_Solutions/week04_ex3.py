from mpi4py import MPI

# Get current rank
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# Get size
size = comm.Get_size()


# a)
if rank == 0:
    ret = [rank + 2]
    for source in range(1, size):
        ret.append(comm.recv(source=source))
    print(ret)
else:
    comm.send(rank + 2, dest=0)


# b)
ret = comm.gather(rank + 2, root=0)
if rank == 0:
    print(ret)
