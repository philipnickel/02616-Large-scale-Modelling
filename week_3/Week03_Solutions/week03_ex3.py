import sys
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
    """
    if NP == 0:
        return [], []
    return zip(*[mp.Pipe(duplex) for _ in range(NP)])

connections = [[None] * NP for _ in range(NP)]
# create connections
for rank in range(NP):
    # create the connection between rank and a corresponding node
    c1s, c2s = create_connections(NP-rank-1, True)
    for to_rank, (c1, c2) in enumerate(zip(c1s, c2s), rank + 1):
        connections[rank][to_rank] = c1
        connections[to_rank][rank] = c2


def gather_a(rank, conn):

    if rank == 0:
        ret = []
        # send first, then recv
        for from_rank in range(1, NP):
            # from_rank is present to debug things
            ret.append(conn.recv())
        print(f"{ret = }")
    else:
        # all other just sends to the first rank
        conn.send(rank + 2)

def gather_b(rank, conns):

    if rank == 0:
        ret = []
        # send first, then recv
        for from_rank, conn in enumerate(conns[1:], 1):
            # from_rank is present to debug things
            ret.append(conn.recv())
        print(f"{ret = }")
    else:
        # all other just sends to the first rank
        conns[0].send(rank + 2)


with mp.Pool(NP) as pool:

    # the pair is this one
    c_to = connections[0][1]
    # note that *all* sending ranks are using the same connection
    # *Just to show you can*.
    c_from = connections[1][0]
    pool.starmap(gather_a, zip(range(NP), [c_to] + [c_from] * NP))
    pool.starmap(gather_b, zip(range(NP), connections))

# this also calls close on the connections
del connections
