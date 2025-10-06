import sys
from time import perf_counter as time
import multiprocessing as mp

mp.set_start_method("fork")

# Number of processors
NP = 4
if len(sys.argv) > 1:
    NP = int(sys.argv[1])
assert NP > 1, "Minimally 2 processors required"

def create_connections(NP, duplex: bool=False):
    """Create a tuple of ``receive, sends`` objects from a
    `multiprocessing.Pipe` call.

    This is functionally equivalent to:

    >>> recvs, sends = [], []
    >>> for _ in range(NP):
    ...     recv, send = mp.Pipe(duplex)
    ...     recvs.append(recv)
    ...     sends.append(send)
    >>> return recvs, sends
    """
    return zip(*[mp.Pipe(duplex) for _ in range(NP)])

recvs, sends = create_connections(NP)

# cycle the send arrays to make a ring
sends = list(sends[1:]) + [sends[0]]

# Now create the loop
def ring(rank, recv, send):
    if rank == 0:
        print(f"{rank} sending")
        # send first, then recv
        send.send(0)
        print(f"{rank} receiving")
        ret = recv.recv()
        print("done: ")
        print(ret)
    else:
        print(f"{rank} receiving")
        v = recv.recv()
        print(f"{rank} sending")
        send.send(v + 1)


with mp.Pool(NP) as pool:

    t0 = time()
    pool.starmap(ring, zip(range(NP), recvs, sends))
    print(f"ring = {NP}  {time() - t0}")

# this also calls close on the connections
del recvs, sends
