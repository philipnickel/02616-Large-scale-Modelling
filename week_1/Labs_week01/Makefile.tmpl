SRCS = hello_c.c 
OBJS = $(SRCS:.c=.o)
TGTS = $(SRCS:.c=) 

CC	= mpicc
DBG	= -g
OPT	= 
CFLAGS	= $(DBG) $(OPT) 

define make-target
$1: $!.o
	$(CC) $(CFLAGS) -o $@ $<
endef

all: $(TGTS)
	$(foreach t , $(TGTS), $(eval $(call make--target,$(t))))

clean:
	@/bin/rm -f $(OBJS)

realclean: clean
	@/bin/rm -f $(TGTS)
