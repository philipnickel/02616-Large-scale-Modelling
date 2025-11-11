# Custom data-types

Up till now we've only played with *basic* data-types.

In todays exercise we will concentrate on extending data-types to
create custom data-types for sending segments of arrays.

Again, use these pages:

- https://mpi4py.readthedocs.io/en/stable/reference/mpi4py.MPI.Comm.html
- https://docs.open-mpi.org/en/v5.0.x/man-openmpi/man3/index.html

and finally, [this page](https://www.hlrs.de/training/self-study-materials/mpi-course-material)
for additional training material/explanations, there are some even more advanced.


The modules you should use are these:
```shell
module load matplotlib/3.10.3-numpy-2.3.1-python-3.12.11
module load mpi4py/4.0.3-python-3.12.11-openmpi-5.0.8
```

## Exercises

In todays exercises we are mainly interested in how data is being sent.

So please re-use the bandwidth plots from week 4 in todays exercises
when playing around with the custom data-types.

You have to implement verification methods that ensures that the transfers
are correct, and that they don't corrupt the receiving array.

You should also play with receiving data in the *basic* element types
and assert that you understand this correctly!


1. *Understanding EXERCISE*

   In `sample.py` an introductory way of using custom data-types for a
   Cartesian coordinate system.

2. Create a data-type where you will only send the $x$, $y$ components.
   And one where you will only send the $x$, $z$ components of the array.

   Do a bandwidth plot (as done for week 4) for these cases:

   1. With a temporary buffer copying the $x$, $z$ components.
   2a. With the custom data-type $x$, $z$.
   2b. With the custom data-type $x$, $y$.

   Plot the bandwidth in all 3 cases.

   Hint: Start with 1 and 2a, 2b requires a *resize* to align the end.

   TIME: Do the custom data-types with both `Create_indexed` and `Create_struct`
         likely, you've used one of them, now use the other.

3. Create a code that deals with matrices.

   In the algorithm you are implementing you have to communicate the edges
   of the matrix.

   In the implementation we require that the implementation creates the
   datatypes depending on the matrix dimensions (N, N).

   1. Implement a data-type that holds the contiguous parts of the matrix.
      (one row)
   2. Implement a data-type that holds the strided parts of the matrix.
      (one column)

   Do a bandwidth benchmark of the above data-types vs. the naive one of
   copying the elements to a buffer.

   TIME: Implement a data-type that holds the top+bottom rows of the matrix
         and also one that holds first+last columns of the matrix.
