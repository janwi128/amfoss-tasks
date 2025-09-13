#include <stdio.h>
#include <string.h>

void search_stream(FILE *f, const char *pattern) {
    char buf[1024];
    while (fgets(buf, sizeof(buf), f) != NULL) {
        if (strstr(buf, pattern) != NULL) {
            fputs(buf, stdout);
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s PATTERN [file...]\n", argv[0]);
        return 2;
    }

    const char *pattern = argv[1];

    if (argc == 2) {
        search_stream(stdin, pattern);
    } else {

        for (int i = 2; i < argc; ++i) {
            FILE *f = fopen(argv[i], "r");
            if (!f) {
                fprintf(stderr, "Could not open file: %s\n", argv[i]);
                continue;
            }
            search_stream(f, pattern);
            fclose(f);
        }
    }

    return 0;
}

/*

Approach:
This command searches for a word inside a file (like a mini grep). I read each line with 
fgets and used strstr to check if the search term exists in that line.

Challenges/Bugs:
One challenge was making sure the program printed the correct lines and handled multiple files. 
Another was understanding how strstr works for substring search.

What I learned:
I learned how string searching works in C, how to scan files line by line, and how tools 
like grep might be implemented at a basic level.
*/
