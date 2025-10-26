import multiprocessing as mp

NP = 4

def reduce_operation(rank, connections):
    if rank == 0:
        print(f"Rank {rank}: Starting reduce operation on rank 0")
        total_sum = 0  # Initial value from rank 0
        print(f"Rank {rank}: Initial value: {total_sum}")

        # Receive and sum values from all other ranks
        for i in range(1, NP):
            value = connections[i][0].recv()  # recv_conn for rank i
            total_sum += value
            print(f"Rank {rank}: Received from rank {i}: {value}, running sum: {total_sum}")

        print(f"Final reduced sum: {total_sum}")
    else:
        value = 10  # Each rank contributes rank * 10
        connections[rank][1].send(value)  # send_conn for this rank
        print(f"Rank {rank}: Sent value {value} to rank 0")

if __name__ == "__main__":
    # Create separate pipes for each non-zero rank to communicate with rank 0
    connections = {}
    for i in range(1, NP):
        recv_conn, send_conn = mp.Pipe(False)
        connections[i] = (recv_conn, send_conn)

    processes = [
        mp.Process(target=reduce_operation, args=(rank, connections))
        for rank in range(NP)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()
