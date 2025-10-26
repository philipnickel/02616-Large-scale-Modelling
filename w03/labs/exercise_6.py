import multiprocessing as mp
import numpy as np
import time
import matplotlib.pyplot as plt
import scienceplots
plt.style.use('science')

def bandwidth_test(rank, conn, array_sizes, results_queue):
    if rank == 0:
        # Sender process
        results = []

        for size in array_sizes:
            # Create random numpy array
            data = np.random.rand(size)
            data_bytes = data.nbytes

            # Time the send operation
            start_time = time.time()
            conn.send(data)

            # Wait for acknowledgment to ensure data was received
            conn.recv()
            end_time = time.time()

            transfer_time = end_time - start_time
            bandwidth_mbps = (data_bytes / (1024**2)) / transfer_time

            print(f"Size: {size} elements ({data_bytes/1024**2:.2f} MB), Time: {transfer_time:.4f}s, Bandwidth: {bandwidth_mbps:.2f} MB/s")
            results.append((data_bytes/1024**2, bandwidth_mbps))

        # Send results back to main process
        results_queue.put(results)

    else:
        # Receiver process
        for size in array_sizes:
            # Receive data
            data = conn.recv()

            # Send acknowledgment
            conn.send("ack")

if __name__ == "__main__":
    # Create array sizes using logspace (from 10^3 to 10^7 elements)
    array_sizes = np.logspace(3, 7, 15, dtype=int)

    # Create pipe for communication
    recv_conn, send_conn = mp.Pipe()

    # Create queue for results
    results_queue = mp.Queue()

    # Create processes
    sender = mp.Process(target=bandwidth_test, args=(0, send_conn, array_sizes, results_queue))
    receiver = mp.Process(target=bandwidth_test, args=(1, recv_conn, array_sizes, results_queue))

    # Start processes
    sender.start()
    receiver.start()

    # Wait for completion
    sender.join()
    receiver.join()

    # Get results from queue
    bandwidth_results = results_queue.get()

    # Plotting the results
    sizes_mb, bandwidths = zip(*bandwidth_results)
    plt.figure(figsize=(10, 6))
    plt.loglog(sizes_mb, bandwidths, marker='o')
    plt.xlabel('Array Size (MB)')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('Bandwidth vs Array Size')
    plt.grid(True, which="both", ls="--")
    plt.show()

