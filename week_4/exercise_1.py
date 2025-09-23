import numpy as np
from mpi4py import MPI
from mpi4py.util.dtlib import from_numpy_dtype

"""
All MPI processes execute their *own* Python process
and thus are completely orthogonal. A fully distributed
process + memory management system.

Can you e.g. launch multiprocessing in your MPI processes?
- probably not if MPIrun binds to specific cores
- Maybe by unbinding the MPI processes from cores or something like that
"""

# A communicator handles the group of processes who can
# communicate together. We will come back to this after
# Project 1
comm = MPI.COMM_WORLD
# Get rank in the `comm` communicator.
rank = comm.Get_rank()
# Get total number of MPI ranks in the `comm` communicator.
size = comm.Get_size()

"""
Sending *Python objects* is done using
the lower-case methods (recv/send/bcast/...).
Sending *buffer objects* (numpy.ndarray) is done
using the title of the method (Recv/Send/Bcast/...).

Always prefer to use *buffer objects*!
"""

# This script only works for size == 2
if size != 2:
    raise RuntimeError("Expected exactly 2 MPI ranks!")

if rank == 0:
    # `tag` can be used to identify messages
    ret = comm.recv(source=rank+1, tag=1)
    print("received: ", ret)
else:
    comm.send(3, dest=0, tag=1)

"""
Dealing with MPI is *only* dealing with *bytes*.
So it is important to know how and how much you Send/Recv things.

One can selectively Send/Recv specific messages
by using `tag` as a message identifier.
And, one can overlap messages and communications by using
*non-blocking* Send/Recv, all non-blocking operations has
the *i<>* equivalent where the `i` stands
for: *immediate* and *incomplete*.

THINK: how do you want to measure bandwidth of non-blocking
       communications?
    -- Sum the bytes from all ranks and divide by the total time?

       Can you measure it when you overlap communications
       and calculations?
    -- be carefull of what is received 

Typically implementations are using the same dtype for
Send/Recv and with the exact length. However, a `Recv`
doesn't know how much data it receives, and therefore
you can request that information through the `MPI.Status` object.
The receiver buffer *can* be larger (but not smaller) than the
received object.
"""

def cut_view(arr, dtype):
    """Create a view by casting `arr` into a specific `dtype`.

    I.e. cast an int8 into a real16.
    If there is a mismatch in the number of elements,
    it will truncate the returned view to the maximum number of
    available elements.
    """
    dtype = np.dtype(dtype)

    # determine how many elements we can host in the view
    elements_per_new = dtype.itemsize // arr.dtype.itemsize

    # Calculate how many elements we can actually host.
    # Since a slice is also a view we are still
    # re-using the same memory location in `arr`.
    # This won't work with complicated slices (e.g. from lists).
    n_elem = arr.size - arr.size % elements_per_new
    return arr[:n_elem].view(dtype=dtype)


"""
Create a timeline of the below code for ranks 0 and 1.
"""


if rank == 0:
    """Our rank == 0 will be the receiving rank"""

    # allocate something that is 1001 bytes
    # how many truncated float32, float64, complex64, complex128 does
    # this equate to?
    buf = np.empty(1001, dtype=np.byte)

    # Message routines with `tag` arguments defaults to `tag=MPI.ANY_TAG`,
    # meaning that it does not distinguish the tag ID.

    comm.Recv(buf, source=rank+1, tag=0)
    # receive in the basic byte/(C char type) dtype
    print("received: ", buf)

    buf_f8 = cut_view(buf, np.float64)
    # receive in the same dtype as is sent.
    # Note, that we don't check here how many elements
    # we actually receive... *bad* practice if you are
    # not careful!
    comm.Recv(buf_f8, source=rank+1, tag=1)
    print("received: ", buf_f8)


    buf_c16 = cut_view(buf, np.complex128)
    # receive in a bigger dtype then what is sent.
    comm.Recv(buf, source=rank+1, tag=3)
    print("received: ", buf_c16)


    # Check the size of the received data
    # Proper check of how many elements we are actually
    # receiving.
    status = MPI.Status()
    comm.Recv(buf_f8, source=rank+1, status=status, tag=4)
    # The `status` object only knows how many *bytes*
    # it has received, transfer that to a specific
    # data type. Either use `mpi4py.util.dtlib.from_numpy_dtype`
    # or know the exact MPI datatype:
    #  MPI.DOUBLE_PRECISION
    n_recv = status.Get_elements(from_numpy_dtype(buf_f8.dtype))
    print(f"received: tag={status.Get_tag()} ", buf_f8[:n_recv])

    status = MPI.Status()
    comm.Recv(buf_c16, source=rank+1, status=status, tag=2)
    # Either use `mpi4py.util.dtlib.from_numpy_dtype`
    # or know the exact MPI datatype:
    #  MPI.DOUBLE_COMPLEX
    n_recv = status.Get_elements(from_numpy_dtype(buf_c16.dtype))
    print(f"received: tag={status.Get_tag()} ", buf_c16[:n_recv])

else:
    """ rank == 1 will be the sender of data! """

    # Create a float64 array:
    arr = np.arange(100, dtype=np.float64)
    # end the same array multiple times
    reqs = []
    for i in range(5):
        # Non-blocking send using distinct tags.
        # In which order are the messages received on rank==0?
        # note we store the requests to ensure they are completed
        # before we can delete them!
        req = comm.Isend(arr[:-i], dest=0, tag=i)
        reqs.append(req)

    # Wait for all communication requests
    # check documentation, the status argument is MPI_STATUSES_IGNORE
    MPI.Request.waitall(reqs)

    # The Request objects are allocated in C-memory.
    # And the mpi4py does not have automatic garbage-collection!
    # This only works in mpi4py>=4
    for req in reqs:
        req.free()
