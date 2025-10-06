import multiprocessing as mp

NP = 4

def broadcast(rank, connections):
    if rank == 0:
        data = "Broadcast message from rank 0"
        print(f"Rank {rank}: Broadcasting: {data}")

        # Send to all other ranks
        for i in range(1, NP):
            connections[i][1].send(data)  # send_conn for rank i
            print(f"Rank {rank}: Sent to rank {i}: {data}")
    else:
        # Receive from rank 0
        data = connections[rank][0].recv()  # recv_conn for this rank
        print(f"Rank {rank}: Received from rank 0: {data}")

if __name__ == "__main__":
    # Create separate pipes for each non-zero rank to communicate with rank 0
    connections = {}
    for i in range(1, NP):
        recv_conn, send_conn = mp.Pipe(False)
        connections[i] = (recv_conn, send_conn)

    processes = [
        mp.Process(target=broadcast, args=(rank, connections))
        for rank in range(NP)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join() 
