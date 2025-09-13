#include <stdio.h>
#include <dirent.h>

int main(int argc, char *argv[]) {
    const char *path = (argc > 1) ? argv[1] : ".";

    DIR *dir = opendir(path);
    if (!dir) {
        printf("Could not open directory: %s\n", path);
        return 1;}

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        printf("%s\n", entry->d_name);
    }

    closedir(dir);

    return 0;
}

/*
Approach:
I implemented listit using the <dirent.h> library, which allows reading directory contents. 
The program opens a directory, iterates through its entries, and prints out each file or 
folder name, similar to the ls command.

Challenges/Bugs:
Initially, I faced a compilation error because I mistakenly wrote #include <dirent.> instead 
of #include <dirent.h>. Once corrected, the program worked.

What I learned:
I learned how to use directory-related functions like opendir, readdir, and closedir, and 
how C handles directory traversal.
*/
