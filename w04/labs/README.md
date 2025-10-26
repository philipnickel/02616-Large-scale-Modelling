# Introduction to mpi4py

mpi4py is the layer that binds the MPI library (that you played
with in week 1 + 2) into Python objects.

We will use the same exercises as last week, but will convert
them to mpi4py.

See here for additional learning material:
https://www.hlrs.de/training/self-study-materials/mpi-course-material

Use [this page](https://mpi4py.readthedocs.io/en/stable/reference/mpi4py.MPI.Comm.html)
and [this page](https://docs.open-mpi.org/en/v5.0.x/man-openmpi/man3/index.html)
for reference of the methods you'll use throughout these exercises.
In particular you'll have to read the documentation of these methods
(preferably both on the OpenMPI *and* `mpi4py` documentation pages):
- `MPI_Isend` / `isend`
- `MPI_Recv` / `recv`
- `MPI_Bcast` / `bcast`
- `MPI_Gather` / `gather`
- `MPI_Reduce` / `reduce`

Please remember that `mpi4py` is case sensitive!


## Exercises

For those exercises where we ask you to do benchmarks (e.g. bandwidth plots)
you should use the HPC facility, otherwise you *can* do the exercises on
your laptop. To oversubscribe the number of MPI ranks in the job
you can use `mpirun --oversubscribe` to allow it to allocate
more cores than you have available. This can be beneficial for testing
purposes, but should otherwise not be used!


1. *Understanding EXERCISE*

   `sample.py`. An example of how to do simple messaging using `mpi4py`.

   Please be sure to answer the five questions asked in the comments
   of the code.

   To run it, do:

   ```shell
   mpirun -np X python3 sample.py

   ```
   to run it using `X` number of processors.

2. Create a code where you'll create a ring communication.

   So every rank sends information to `rank+1`, except the last
   rank which sends to `rank==0`.

   The `rank==0` starts to send the data.

3. Create a code where the first `rank` process is gathering
   results.

   - receiving some values from all *other* ranks
   - stores the values in a list
   - finally, printing out the list.

   a) do one with manual `send`/`recv`.

   b) do one with the collective `gather` operation.

4. Create a code where you'll distribute/broadcast the same numpy array from
   the first rank to all others.

   a) do one with manual `Isend`/`Recv` using specific tags.
   b) do one with the collective `Bcast` operation.

   Do a bandwidth plot of both, consider which rank you should plot?

5. Create a code where you'll `reduce` some values on a single rank.
   This is similar to 3., but instead of accumulating a list, you'll sum
   the values received into a single value.

   Note, that when using MPI, you should provide your own callable for Python
   objects, e.g. `lambda a, b: a+b`.
   For numpy arrays, simply use an MPI-type operator (e.g. `MPI.SUM`).

6. Using 2 processes create a code to extract the transport bandwidth
   of numpy arrays.

   The (log-log) plot should have the $x$-axis with the message size in bytes or MB, and
   the $y$-axis with MB/s.

   Compare this with last weeks exercises bandwidth plots.
