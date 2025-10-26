from mpi4py import MPI

# Get current rank
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
# Get size
size = comm.Get_size()


def ring_simple():
    if rank == 0:
        comm.send(rank+1, dest=rank + 1)
    ret = comm.recv(source=(rank - 1) % size)
    if rank != 0:
        comm.send(ret, dest=(rank + 1) % size)
    else:
        print(ret)

def ring_sendrecv():
    dest = (rank + 1) % size
    source = (rank - 1) % size
    ret = comm.sendrecv(rank+1,
                        dest=dest, sendtag=rank,
                        source=source, recvtag=source
                  )
    if rank == 0:
        print(ret)


ring_simple()
ring_sendrecv()
