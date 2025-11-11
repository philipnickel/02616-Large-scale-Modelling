# Communicators and groups

Up till now we've only played with *global* communication.

In todays exercise we will concentrate on playing with *creating*
new communicators. Either from existing ones (the easiest), or from
a group construction.

Again, use these pages:

- <https://mpi4py.readthedocs.io/en/stable/reference/mpi4py.MPI.Comm.html>
- <https://docs.open-mpi.org/en/v5.0.x/man-openmpi/man3/index.html>

and finally,

- <https://www.hlrs.de/training/self-study-materials/mpi-course-material>
for additional training material/explanations.

The modules you should use are these:

```shell
module load matplotlib/3.10.3-numpy-2.3.1-python-3.12.11
module load mpi4py/4.0.3-python-3.12.11-openmpi-5.0.8
```

## Exercises

In todays exercises we are not too interested in performance. It may
be useful to test these things on your own laptop for faster throughput.
Please remember to oversubscribe the MPI ranks by `mpirun --oversubscribe`.

Again, please only use *oversubscription* for testing purposes!

1. *Understanding EXERCISE*

   `sample.py`. An example of how to do simple manipulation of communicators.

   To run it, do:

   ```shell
   mpirun -np X python3 sample.py
   ```

   to run it using `X` number of processors.

   In the following exercises, please use the `print_comm_info` as a reference
   to print out information on the communicators.

2. Create a code where you will split the world communicator into
   3 communicators.

   You should do this in two different ways:

   1. Where every 3rd rank belongs to the same new communicator.
   2. Where the new communicator is created from a continuous set of ranks.

   In both of the above cases, do it:

   1. using `Comm.Split`
   2. using groups, choose yourself by which method you'll create sub-groups.

   Run this code at 8, 7 and 9 ranks.

   It shouldn't break!

3. Create a code where you'll first split the world communicator
   in 2, then split that communicator in 2.

   Do this for, at least, 3, 4 and 10 ranks.
   Also, draw this using sets on a piece of paper.

4. Create a code where you'll distribute a set of ranks into a 2D grid
   using `Create_cart`.

   Do this for ranks = 4, 9, 26 (the code shouldn't break!).

   Draw the grids on a piece of paper and pre-determine how `comm.Shift` will
   behave in the following product of situations:

   1. With `periods` as both `True` and `False`
   2. With a center rank in the grid (agreed, there is no center for 2x2 grids).
   3. With displacements of -2, 1, 2.

   Correlate with what you did by pen and paper. Are they commensurate?
