import numpy as np
from mpi4py import MPI

"""
In MPI we've used `MPI.COMM_WORLD` which is the default
communicator encompassing *all* available ranks.

When working with communicators (and generally always), never use
MPI.COMM_WORLD. If you have to extend the library/routines later
down the road, it is better to have a variable that can be changed.

So, if you want to use COMM_WORLD, clone it!
"""
comm = MPI.COMM_WORLD.Clone()


def print_comm_info(comm: MPI.Comm, ref_comm: MPI.Comm | None = None, info: str = ""):
    """Simple information printer of the communicator information"""

    # Determine if we are a valid communicator
    is_valid = comm != MPI.COMM_NULL
    proc_name = MPI.Get_processor_name()

    if is_valid:
        # Extract the rank in a *parent* communicator!
        rank = comm.Get_rank()
        size = comm.Get_size()
    else:
        # Assign *non-valid ranks*.
        rank = size = -1

    if ref_comm:
        ref_rank = ref_comm.rank
        ref_size = ref_comm.size
        print(f"{info:20s} | {proc_name}:   {rank}/{size}  [{ref_rank}/{ref_size}]")
    else:
        print(f"{info:20s} | {proc_name}:   {rank}/{size}")


# Print info for world communicator!
print_comm_info(comm, info="Comm_World")


"""
Now, we can split the communicator in two.
This can be done in numerous ways, but we'll just take
every second rank to be in either communicator.
"""
comm_half = comm.Split(comm.Get_rank() % 2)
print_comm_info(comm_half, info="Split in half")

"""
One can also create groups and re-arrange the ranks, in this a bit odd construct.
"""
group_world = comm.Get_group()
group_rearranged = group_world.Range_incl([(group_world.size - 1, 0, -1)])
comm_rearranged = comm.Create_group(group_rearranged)
print_comm_info(comm_rearranged, comm, info="World, re-arranged")
