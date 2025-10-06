from mpi4py import MPI
from time import perf_counter as time
import numpy as np

# Number of processors
comm = MPI.COMM_WORLD

rank = comm.Get_rank()
NP = comm.Get_size()
assert NP == 2, "Only 2 processors allowed"

def bandwidth_window(rank, N, window: int=12):
    kbs = np.logspace(0, 6, num=N)
    # Max elements
    max_n = int(kbs[-1] * 1024 / 8)
    buffer = np.zeros(max_n, dtype=np.float64)
    mb = []
    s = []
    reqs = [None] * window

    if rank == 0:
        status = MPI.Status()
        for kb in kbs:
            # elements
            n = int(kb * 1024 / 8)
            t0 = time()
            for i in range(window):
                req = comm.Irecv((buffer, n, MPI.DOUBLE), 1, tag=window)
                reqs[i] = req
            MPI.Request.Waitall(reqs)
            s.append(time() - t0)
            try:
                for req in reqs:
                    req.Free()
            except: pass
            mb.append(status.Get_count() / 1024 ** 2) # MB
    else:

        for kb in kbs:
            # elements
            n = int(kb * 1024 / 8)
            t0 = time()
            for i in range(window):
                req = comm.Isend((buffer, n, MPI.DOUBLE), 0, tag=window)
                reqs[i] = req
            MPI.Request.Waitall(reqs)
            s.append(time() - t0)
            try:
                for req in reqs:
                    req.Free()
            except: pass
            mb.append(n * 8 / 1024 ** 2) # MB
    mb = np.asarray(mb)
    return mb, mb/s


def bandwidth(rank, N):
    kbs = np.logspace(0, 6, num=N)
    # Max elements
    max_n = int(kbs[-1] * 1024 / 8)
    buffer = np.zeros(max_n, dtype=np.float64)
    mb = []
    s = []

    if rank == 0:
        status = MPI.Status()
        for kb in kbs:
            # elements
            n = int(kb * 1024 / 8)
            t0 = time()
            comm.Recv((buffer, n, MPI.DOUBLE), 1, tag=0, status=status)
            s.append(time() - t0)
            mb.append(status.Get_count() / 1024 ** 2) # MB
    else:

        for kb in kbs:
            # elements
            n = int(kb * 1024 / 8)
            t0 = time()
            comm.Send((buffer, n, MPI.DOUBLE), 0, tag=0)
            s.append(time() - t0)
            mb.append(n * 8 / 1024 ** 2) # MB
    mb = np.asarray(mb)
    return mb, mb/s

from matplotlib import pyplot as plt

N = 12
mb, mb_s = bandwidth(rank, N)
plt.plot(mb, mb_s, label="1")

for w in [2, 4, 8, 16, 32]:
    mbw, mbw_s = bandwidth_window(rank, N, w)
    plt.plot(mbw, mbw_s, label=f"{w}")

plt.loglog()
plt.legend()
plt.xlabel("Array size in MB")
plt.ylabel(f"Bandwidth MB/s")
plt.savefig(f"bandwidth_{rank}.png")
plt.show()
