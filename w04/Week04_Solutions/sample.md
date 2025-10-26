

Here are the answers to the questions outlined in the `sample.py`
file.


> Can you e.g. launch multiprocessing in your MPI processes?

Yes you can! You'll then have access to a *local node* multiprocessing
functionality, together with MPI.
This is called a *hybrid MPI* program that utilizes more than
one parallel paradigm.


> How do you want to measure bandwidth of non-blocking
> communications?
>
> Can you measure it when you overlap communications
> and calculations?

It's hard, sometimes you basically can't. If there is
no overlap between communications and calculations,
you can time before you post the communication,
and just after your `Wait`. In which case it will
be correct for *all* messages sent/received.

However, if you have calculations interleaved in
your communication, then you are never fully
sure if the communication happened at the same
time of the calculation, or whether they would be
synchronized separate calls. I.e. you can't time it.


> How many truncated float32, float64, complex64, complex128 does
> this equate to?

The allocation is $1001$ bytes, the datatypes occupy the number
of bits in their names, hence a float32 is 32 bits = (4*8) bits = 4 bytes.
Then simply divide by how many bytes they are:

1001 // 4 == 250, 1 byte unused
1001 // 8 == 125, 1 byte unused
1001 // 16 == 62, 9 bytes unused


> In which order are the messages received on rank==0?

The non-blocking sends are sent in consecutive order (`tag`).
However, rank==0 receives them in this order (and # of bytes/dtypes):

1. tag == 0, sending/receiving 800 bytes
2. tag == 1, sending/receiving 792 bytes == 99 float64
3. tag == 3, sending/receiving 776 bytes == 48.5 complex128
4. tag == 4, sending/receiving 768 bytes == 96 float64
5. tag == 2, sending/receiving 784 bytes == 49 complex128

