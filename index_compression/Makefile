CC = gcc
CFLAGS = -pedantic -Wall -std=gnu99
BIN = make_index
SRC = main.c
all: $(BIN)

$(BIN): $(SRC)
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)

clean:
	$(RM) $(BIN)
