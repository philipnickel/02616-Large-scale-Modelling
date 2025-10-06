import multiprocessing as mp

NP = 3

def ring_process(rank, recv_conn, send_conn):
    if rank == 0:
        print(f"Rank {rank}: Starting ring")
        send_conn.send("Hello from rank 0")
        data = recv_conn.recv()
        print(f"Rank {rank}: Received back: {data}")
    else:
        data = recv_conn.recv()
        new_data = f"{data} -> rank {rank}"
        send_conn.send(new_data)
        print(f"Rank {rank}: Forwarded: {new_data}")

if __name__ == "__main__":
    recv_conns, send_conns = zip(*[mp.Pipe(False) for _ in range(NP)])

    processes = [
        mp.Process(target=ring_process, args=(rank, recv_conns[rank], send_conns[(rank + 1) % NP]))
        for rank in range(NP)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()
