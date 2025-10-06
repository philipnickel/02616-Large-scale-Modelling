import multiprocessing as mp

# Exercise 2: Ring Communication Implementation
#
# Ring Communication Pattern:
# - N processes form a ring where each sends to the next: 0→1→2→3→0
# - Rank 0 starts by sending initial data
# - Each rank receives the message, adds its identifier, and forwards it
# - The message travels around the ring back to rank 0
#
# Answer to "How many connections required at minimum?":
# You need exactly N connections for N processes - one connection per process
# to create the ring topology.

NP = 4  # Number of processors in the ring

def create_connections(NP: int, duplex: bool=False):
    """Create a tuple of ``receive, sends`` of `NP` objects from a
    `multiprocessing.Pipe` call.
    `duplex` controls whether the communication is bidirectional.
    """
    return zip(*[mp.Pipe(duplex) for _ in range(NP)])


def message(rank, recv_conn, send_conn):
    """Simplified message function for ring communication"""
    if rank == 0:
        # Start the ring by sending initial data
        print(f"Rank {rank}: Starting ring")
        send_conn.send("Hello from rank 0")

        # Receive the message after it travels around the ring
        data = recv_conn.recv()
        print(f"Rank {rank}: Received back: {data}")
        return data
    else:
        # All other ranks receive, process, and forward
        data = recv_conn.recv()
        print(f"Rank {rank}: Received: {data}")

        # Add to the message and send to next
        new_data = f"{data} -> passed through rank {rank}"
        send_conn.send(new_data)
        print(f"Rank {rank}: Forwarded: {new_data}")

def ring_process(rank, recv_conn, send_conn):
    """Each process in the ring - simplified to use message function"""
    message(rank, recv_conn, send_conn)

if __name__ == "__main__":
    # Create ring connections: each process sends to (rank+1) % NP
    # Using Pool: 
    recv_conns, send_conns = create_connections(NP, duplex=False)
    recv_conns = list(recv_conns)
    send_conns = list(send_conns)
    with mp.Pool(NP) as pool:
        pool.starmap(ring_process, 
                     [(rank, recv_conns[rank], send_conns[(rank + 1) % NP]) for rank in range(NP)])



