#!/usr/bin/env python3
"""
Exercise 6: Bandwidth measurement using 2 processes
Extract the transport bandwidth of numpy arrays with log-log plots.
x-axis: message size in bytes or MB
y-axis: MB/s
"""

from mpi4py import MPI
import numpy as np
import time
import matplotlib.pyplot as plt

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if size != 2:
    raise RuntimeError("This exercise requires exactly 2 MPI processes! Run with: mpirun -np 2 python3 exercise_6.py")

# Message sizes to test (powers of 2 from 2^10 to 2^24 bytes)
min_power = 10
max_power = 24
message_sizes = [2**i for i in range(min_power, max_power + 1)]

# Number of repetitions for each size to get average
num_repetitions = 10

print(f"Rank {rank}: Starting bandwidth measurement")
print(f"Testing message sizes from {2**min_power} to {2**max_power} bytes")

bandwidths = []
message_sizes_mb = []

for msg_size in message_sizes:
    # Create data arrays
    if rank == 0:
        send_data = np.random.random(msg_size // 8).astype(np.float64)  # 8 bytes per float64
        recv_data = np.empty(msg_size // 8, dtype=np.float64)
    else:
        send_data = np.random.random(msg_size // 8).astype(np.float64)
        recv_data = np.empty(msg_size // 8, dtype=np.float64)

    # Warm-up run
    if rank == 0:
        comm.Send(send_data, dest=1, tag=0)
        comm.Recv(recv_data, source=1, tag=1)
    else:
        comm.Recv(recv_data, source=0, tag=0)
        comm.Send(send_data, dest=0, tag=1)

    # Synchronize before timing
    comm.Barrier()

    # Measure bandwidth over multiple repetitions
    total_time = 0.0

    for rep in range(num_repetitions):
        start_time = time.time()

        if rank == 0:
            # Send data to rank 1 and receive it back
            comm.Send(send_data, dest=1, tag=rep*2)
            comm.Recv(recv_data, source=1, tag=rep*2+1)
        else:
            # Receive data from rank 0 and send it back
            comm.Recv(recv_data, source=0, tag=rep*2)
            comm.Send(send_data, dest=0, tag=rep*2+1)

        end_time = time.time()
        total_time += (end_time - start_time)

    # Calculate bandwidth (round trip, so 2 * message size)
    avg_time = total_time / num_repetitions
    bytes_transferred = 2 * msg_size  # Round trip
    bandwidth_mbps = (bytes_transferred / avg_time) / (1024 * 1024)  # MB/s

    if rank == 0:
        bandwidths.append(bandwidth_mbps)
        message_sizes_mb.append(msg_size / (1024 * 1024))  # Convert to MB
        print(f"Message size: {msg_size:8d} bytes ({msg_size/(1024*1024):6.2f} MB), "
              f"Avg time: {avg_time*1000:8.3f} ms, Bandwidth: {bandwidth_mbps:8.2f} MB/s")

# Plot results (only rank 0)
if rank == 0:
    plt.figure(figsize=(10, 6))
    plt.loglog(message_sizes_mb, bandwidths, 'bo-', linewidth=2, markersize=6)
    plt.xlabel('Message Size (MB)')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('MPI Bandwidth Measurement (mpi4py)')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=max(bandwidths), color='r', linestyle='--', alpha=0.7,
                label=f'Peak: {max(bandwidths):.1f} MB/s')
    plt.legend()

    # Save the plot
    plt.savefig('bandwidth_plot.png', dpi=300, bbox_inches='tight')
    print(f"Rank {rank}: Plot saved as 'bandwidth_plot.png'")

    # Print summary statistics
    print(f"\nBandwidth Summary:")
    print(f"Peak bandwidth: {max(bandwidths):.2f} MB/s")
    print(f"Average bandwidth: {np.mean(bandwidths):.2f} MB/s")
    print(f"Bandwidth at 1MB: {bandwidths[message_sizes_mb.index(min(message_sizes_mb, key=lambda x:abs(x-1.0)))]:.2f} MB/s")

print(f"Rank {rank}: Bandwidth measurement completed")