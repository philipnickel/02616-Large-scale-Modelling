/*
 * Copyright (c) 2004-2006 The Trustees of Indiana University and Indiana
 *                         University Research and Technology
 *                         Corporation.  All rights reserved.
 * Copyright (c) 2006      Cisco Systems, Inc.  All rights reserved.
 *
 * Sample MPI "hello world" application in C
 */

#include <stdio.h>
#include "mpi.h"

int
main(int argc, char* argv[]) {

    int rank, size;
    int message;
    int tag = 100;
    MPI_Status status;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    printf("Hello, world from %d of %d!\n", rank, size);

    /* Implement Send/Recv communication pattern */
    if (rank % 2 == 0) {
        /* Even ranks send to next rank (if it exists) */
        if (rank + 1 < size) {
            message = rank * 100;  /* Send rank-specific data */
            printf("Process %d sending message %d to process %d\n",
                   rank, message, rank + 1);
            MPI_Send(&message, 1, MPI_INT, rank + 1, tag, MPI_COMM_WORLD);
        } else {
            printf("Process %d (even) has no partner to send to\n", rank);
        }
    } else {
        /* Odd ranks receive from previous rank */
        printf("Process %d waiting to receive from process %d\n",
               rank, rank - 1);
        MPI_Recv(&message, 1, MPI_INT, rank - 1, tag, MPI_COMM_WORLD, &status);
        printf("Process %d received message %d from process %d\n",
               rank, message, rank - 1);
    }

    MPI_Finalize();

    return 0;
}
