import multiprocessing as mp

# Store number of processors
# This sample *only works* with 2!
NP = 2
# Create a connection between two end-points.

def message(rank, comm):
    if rank == 0:
        print(f"{rank=} receiving")
        ret = comm.recv()
        print("received: ", ret)
        return ret
    else:
        comm.send(3)

if __name__ == "__main__":

# duplex means whether it is a two-way communication.
    recv, send = mp.Pipe(duplex=False)
# a) Using Pool
    with mp.Pool(2) as pool:
        assert pool.starmap(message, zip(range(2), [recv, send])) is not None, \
                "Actual return values"

# b) Using Process
    processes = []
    processes.append(mp.Process(target=message, args=(0, recv)))
    processes.append(mp.Process(target=message, args=(1, send)))
    for process in processes:
        # start all processes
        process.start()
    for process in processes:
        # ensure they have completed!
        assert process.join() is None, "join should not return anything but None"
    for process in processes:
        # closing them releases all things, we can't do anything again.
        process.close()


