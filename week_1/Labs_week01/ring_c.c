/*
 * Copyright (c) 2004-2006 The Trustees of Indiana University and Indiana
 *                         University Research and Technology
 *                         Corporation.  All rights reserved.
 * Copyright (c) 2006      Cisco Systems, Inc.  All rights reserved.
 *
 * Simple ring test program
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include "mpi.h"

void
mywork(int p) {

    #define LMAX 1000000
    int i;
    for(i = 0; i < p*LMAX; i++) { }
}
#define sleep mywork

int 
main(int argc, char *argv[]) {

    int rank, size, next, prev, message, tag = 201;
    int no_of_msgs = 10;
    int pause = 0;
    if (argc >= 2) pause = atoi(argv[1]);
    if (argc == 3) no_of_msgs = atoi(argv[2]);

    /* Start up MPI */

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
 
    /* Calculate the rank of the next/prev process in the ring.  */

    next = (rank + 1);
    prev = (rank - 1);

    /* If we are the "master" process (i.e., MPI_COMM_WORLD rank 0),
       put the number of times to go around the ring in the
       message. */
    if (0 == rank) {
        message = no_of_msgs;

        printf("Process 0 sending %d to %d, tag %d (%d processes in ring)\n", 
               message, next, tag, size);
        MPI_Send(&message, 1, MPI_INT, next, tag, MPI_COMM_WORLD); 
        printf("Process 0 sent to %d\n", next);
    }

    /* Pass the message around the ring.  The exit mechanism works as
       follows: the message (a positive integer) is passed around the
       ring.  Each time it passes rank 0, it is decremented.  When
       each processes receives a message containing a 0 value, it
       passes the message on to the next process and then quits.  By
       passing the 0 message first, every process gets the 0 message
       and can quit normally. */

    while (1) {
        MPI_Recv(&message, 1, MPI_INT, prev, tag, MPI_COMM_WORLD, 
                 MPI_STATUS_IGNORE);

        if (0 == rank) {
            --message;
            printf("\nProcess 0 decremented value: %d\n", message);
        }

	sleep(pause);
	printf("%u: Rank %d sending value %d to next rank %d\n", 
	        time(NULL), rank, message, next);

        MPI_Send(&message, 1, MPI_INT, next, tag, MPI_COMM_WORLD);
        if (0 == message) {
            printf("Process %d exiting\n", rank);
            break;
        }
    }

    /* The last process does one extra send to process 0, which needs
       to be received before the program can exit */

    if (0 == rank) {
        MPI_Recv(&message, 1, MPI_INT, prev, tag, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
    }
    
    /* All done */

    MPI_Finalize();
    return 0;
}
