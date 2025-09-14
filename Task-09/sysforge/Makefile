CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra
BIN = bin
SRC = src

all: $(BIN)/listit $(BIN)/showtext $(BIN)/countit $(BIN)/finder

$(BIN)/listit: $(SRC)/listit.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

$(BIN)/showtext: $(SRC)/showtext.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

$(BIN)/countit: $(SRC)/countit.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

$(BIN)/finder: $(SRC)/finder.c | $(BIN)
	$(CC) $(CFLAGS) -o $@ $<

$(BIN):
	mkdir -p $(BIN)

clean:
	rm -f $(BIN)/*

