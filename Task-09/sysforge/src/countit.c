#include <stdio.h>
#include <ctype.h>

void count_file(const char *path) {
    FILE *f = path ? fopen(path, "r") : stdin;
    if (!f) {
        fprintf(stderr, "Could not open file: %s\n", path);
        return;
    }

    long lines = 0, words = 0, chars = 0;
    int c, in_word = 0;

    while ((c = fgetc(f)) != EOF) {
        chars++;
        if (c == '\n') lines++;
        if (isspace((unsigned char)c)) {
            in_word = 0;
        } else if (!in_word) {
            words++;
            in_word = 1;
        }
    }

    if (path) fclose(f);

    printf("%7ld %7ld %7ld", lines, words, chars);
    if (path) printf(" %s", path);
    printf("\n");
}

int main(int argc, char *argv[]) {
    if (argc == 1) {
        count_file(NULL);
    } else {
        for (int i = 1; i < argc; i++) {
            count_file(argv[i]);
        }
    }
    return 0;
}

/*
Approach:
This tool counts lines, words, and characters in a file, similar to the wc command. 
I used fgetc to process each character and added logic to detect word boundaries.

Challenges/Bugs:
A challenge was ensuring correct word counting—especially when there were multiple spaces. 
I solved it by using a flag (in_word) to track when we are inside or outside a word.

What I learned:
I learned about character-level file reading and how to implement logic for word counting.
*/
