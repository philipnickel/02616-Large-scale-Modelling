import sys
import multiprocessing as mp
from time import perf_counter as time
import numpy as np

mp.set_start_method("fork")

# Number of processors
NP = 4
if len(sys.argv) > 1:
    NP = int(sys.argv[1])
assert NP > 1, "Minimally 2 processors required"

def create_connections(NP, duplex: bool=False):
    """Create a tuple of ``receive, sends`` objects from a
    `multiprocessing.Pipe` call.
    """
    return zip(*[mp.Pipe(duplex) for _ in range(NP)])

connections = [[None] * NP for _ in range(NP)]
# create connections
for rank in range(NP):
    # create the connection between rank and a corresponding node
    c1s, c2s = create_connections(NP, True)
    for to_rank, (c1, c2) in enumerate(zip(c1s[rank:], c2s[rank:]), rank):
        connections[rank][to_rank] = c1
        connections[to_rank][rank] = c2


def bcast_single(rank, conns):
    """Only do communication from *one* rank to all others"""
    if rank == 0:
        arr = np.zeros(10) + 1
        # send first
        for from_rank, conn in enumerate(conns[1:], 1):
            # from_rank is present to debug things
            conn.send(arr)
    else:
        arr = conns[0].recv()

    if rank == len(conns) - 1:
        print(arr)

def bcast_chain(rank, conns):
    """Let everybody do chained communication (binary tree)"""

    if rank == 0:
        arr = np.zeros(10) + 1
        conns[rank+1].send(arr)
    elif rank + 1 < len(conns):
        # middle ranks should first receive, *then* send!
        arr = conns[rank-1].recv()
        conns[rank+1].send(arr)
    else:
        # last one only receives
        arr = conns[rank-1].recv()

    if rank == len(conns) - 1:
        print(arr)

with mp.Pool(NP) as pool:

    t0 = time()
    pool.starmap(bcast_single, zip(range(NP), connections))
    print(f"bcast_single = {NP}  {time() - t0}")
    t0 = time()
    pool.starmap(bcast_chain, zip(range(NP), connections))
    print(f"bcast_chain = {NP}  {time() - t0}")

# this also calls close on the connections
del connections
