#include <stdio.h>

void print_file(const char *path) {
    FILE *f = path ? fopen(path, "r") : stdin;

    if (!f) {
        fprintf(stderr, "Could not open file: %s\n", path ? path : "stdin");
        return;
    }

    char buf[1024];
    while (fgets(buf, sizeof(buf), f) != NULL) {
        fputs(buf, stdout);
    }

    if (path) fclose(f);
}

int main(int argc, char *argv[]) {
    if (argc == 1) {
        print_file(NULL);
    } else {
        for (int i = 1; i < argc; i++) {
            print_file(argv[i]);
        }
    }

    return 0;
}

/*
Approach:
I used fopen, fgets, and fclose
to open and read files line by line, then print their contents to the terminal. I added 
support for reading multiple files.

Challenges/Bugs:
At first, my code didn’t compile because I had a typo error.
Another issue was implementing for handling multiple files properly was a bit difficult, which I fixed by using a loop over argv.

What I learned:
I practiced file handling in C, including reading line by line and error-checking when 
a file doesn't exist.
*/
