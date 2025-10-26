# Week 1 Programming Fixes Summary

## Fixed Issues

### 1. Ring Communication Bug (ring_c.c)
**Problem**: Neighbor calculations were incorrect, causing array bounds errors
- `next = (rank + 1)` → would exceed array bounds for last process
- `prev = (rank - 1)` → would be -1 for process 0

**Fix**: Added proper modulo arithmetic
```c
next = (rank + 1) % size;
prev = (rank - 1 + size) % size;
```

### 2. Send/Recv Communication (hello_n.c)
**Problem**: Only had basic hello world, no actual communication
**Fix**: Implemented even/odd communication pattern
- Even ranks (0,2,4...) send to next rank
- Odd ranks (1,3,5...) receive from previous rank
- Demonstrates what happens with different process counts

### 3. Hello World Enhancement (hello_world.c)
**Problem**: Missing `MPI_Comm_size()` call
**Fix**: Added size variable and proper output format

### 4. Makefile Issues
**Problems**:
- Wrong source file name (`hello_c.c` vs `hello_world.c`)
- Syntax errors in make function (`$!.o` should be `$1.o`)
- Missing object file compilation rule
- Typo in function call (`make--target` vs `make-target`)

**Fixes**:
- Corrected source file list
- Fixed make function syntax
- Added `%.o: %.c` rule for object compilation
- Fixed function call syntax

## Testing Instructions

### On HPC Cluster (you'll do this part):
```bash
# Load MPI module
module load mpi/5.0.8-gcc-13.4.0-binutils-2.44

# Compile programs
make clean
make

# Test hello_world
mpirun -np 4 ./hello_world

# Test hello_n with different process counts
mpirun -np 1 ./hello_n  # Should show: no communication (only process 0)
mpirun -np 3 ./hello_n  # Should show: 0→1, 2 has no partner
mpirun -np 4 ./hello_n  # Should show: 0→1, 2→3

# Test ring communication
mpirun -np 4 ./ring_c 0 5  # 5 messages around ring with 4 processes
```

## Expected Behavior

### hello_n.c with different process counts:
- **1 process**: Only process 0, no communication
- **3 processes**: 0→1 communication, process 2 has no partner
- **4 processes**: 0→1 and 2→3 communication pairs

### ring_c.c:
- Messages circulate around all processes in ring topology
- Each pass through process 0 decrements counter
- All processes exit when counter reaches 0

## Key Learning Points
1. **Ring topology**: Every process has exactly two neighbors
2. **Even/odd pairing**: Common pattern for avoiding deadlocks
3. **Process count dependency**: Communication patterns must handle variable process counts
4. **Modulo arithmetic**: Essential for circular topologies