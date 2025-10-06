import multiprocessing as mp

NP = 3

def gather_process(rank, connections):
    if rank == 0:
        print(f"Rank {rank}: Starting gathering on rank 0")
        gathered_data = []

        # Receive from all other ranks
        for i in range(1, NP):
            data = connections[i][0].recv()  # recv_conn for rank i
            gathered_data.append(data)
            print(f"Rank {rank}: Received from rank {i}: {data}")

        print(f"Gathered: {gathered_data}")
    else:
        data = f"Some value from rank {rank}"
        connections[rank][1].send(data)  # send_conn for this rank
        print(f"Rank {rank}: Sent to Rank 0: {data}")

if __name__ == "__main__":
    # Create separate pipes for each non-zero rank to communicate with rank 0
    connections = {}
    for i in range(1, NP):
        recv_conn, send_conn = mp.Pipe(False)
        connections[i] = (recv_conn, send_conn)

    processes = [
        mp.Process(target=gather_process, args=(rank, connections))
        for rank in range(NP)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join() 
