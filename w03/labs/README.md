# multiprocessing

multiprocessing is a *weak* multi-processor library enabling
quite a bit of flexibility, at the cost of speed and general
purpose.

It is relatively simple to use for generic distribution
tasks; such as doing work on segments of arrays.
However, it is not really built for communicating between
processors (although we can do it as we'll see!).

Today we will be playing around with multiprocessing
to get a feel for what is necessary for communicating
between two processors, but also discover limitations.

The exercises here provides an introductory step to understand
how communication works.


## Exercises

1. *Understanding EXERCISE*

   `sample.py`. An example of how to do simple messaging.

   There are various ways to distribute work in multiprocessing,
   here we show the two most commonly used, `Pool` and manual
   process handling.

   The pool will distribute work on a predefined number of processors,
   but where there can be *any* number of *work batches*.

   I.e. one could use 2 processors to distribute 11 workloads.
   Using `Pool` lets the OS handle the distribution of the
   workloads; it is *not* guaranteed that the workloads will be
   split evenly.

   > One main difference between `Pool` and manual control is that
   > the `Pool` construct has an in-built return value construct,
   > where as the manual approach requires your own gathering
   > of returned data (a `Queue` object).

   Try and read the code in detail and understand each step and
   how it works.

   In the following exercises, draw as much inspiration from this script.

2. Create a code where you'll create a ring communication.

   So every rank sends information to `rank+1`, except the last
   rank which sends to `rank==0`.

   The `rank==0` starts to send the data.

   How many connections would you require at a minimum?

   This small code snippet might be useful:
   ```python
   def create_connections(NP: int, duplex: bool=False):
       """Create a tuple of ``receive, sends`` of `NP` objects from a
       `multiprocessing.Pipe` call.
       `duplex` controls whether the communication is bidirectional.
       """
       return zip(*[mp.Pipe(duplex) for _ in range(NP)])
   ```

3. Create a code where the first `rank` process is gathering
   results.

   - receiving some values from all *other* ranks
   - stores(appends) the values to a list
   - finally, printing out the list.

   a) do the code using the same `send` connection for
      all but the 0th rank.
      Can this cause problems? If so, what problem?
   b) create connections for each rank-combination, and pass
      the correct ones to each rank.

4. Create a code where you'll distribute/broadcast the same value from
   the first rank to all others.

5. Create a code where you'll [reduce](https://docs.python.org/3/library/functools.html#functools.reduce) some values on a single rank.
   This is similar to 3., but instead of accumulating a list, you'll sum
   the values received into a single value.

6. Using 2 processes create a code to extract the transport bandwidth
   of numpy arrays.

   The (log-log) plot should have the $x$-axis with the message size in bytes/MB, and
   the $y$-axis with MB/s.

   Hint: use `np.logspace` for getting proper separated array sizes.
