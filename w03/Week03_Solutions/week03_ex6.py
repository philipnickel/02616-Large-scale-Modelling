import multiprocessing as mp
from time import perf_counter as time
import numpy as np

mp.set_start_method("fork")

# Number of processors
NP = 2
assert NP == 2, "Only 2 processors allowed"

def create_connections(NP, duplex: bool=False):
    """Create a tuple of ``receive, sends`` objects from a
    `multiprocessing.Pipe` call.
    """
    return zip(*[mp.Pipe(duplex) for _ in range(NP)])


# Only one way
recv, send = tuple(map(lambda x: x[0], create_connections(1)))
# With duplex connection
crecv, csend = tuple(map(lambda x: x[0], create_connections(1, True)))

def bandwidth(rank, N, conn):
    if rank == 0:
        mb = []
        s = []
        for _ in range(N):
            s.append(time())
            arr = conn.recv()
            s[-1] = time() - s[-1]
            mb.append(arr.nbytes / 1024 ** 2) # MB
        mb = np.asarray(mb)
        return mb, mb/s
    else:

        for kb in np.logspace(0, 6, num=N):
            # elements
            n = int(kb * 1024 / 8)
            arr = np.zeros(n)
            arr = conn.send(arr)

with mp.Pool(NP) as pool:

    # warm-up
    pool.starmap(bandwidth, zip(range(NP), [12] * NP, [recv, send]))

    mb2, mb_s2 = pool.starmap(bandwidth, zip(range(NP), [32] * NP, [crecv, csend]))[0]
    mb, mb_s = pool.starmap(bandwidth, zip(range(NP), [32] * NP, [recv, send]))[0]

from matplotlib import pyplot as plt

plt.plot(mb, mb_s, label="Simplex")
plt.plot(mb2, mb_s2, label="Duplex")
plt.loglog()
plt.xlabel("Array size in MB")
plt.ylabel("Bandwidth MB/s")
plt.legend()
plt.show()
