/*
 * Tiny wrapper — runs the hidden checker. Source removed after build.
 * Compile with: cc -DCHECK_SCRIPT=\"/path/to/check.py\" -o check check_stub.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef CHECK_SCRIPT
#error "CHECK_SCRIPT must be defined at compile time"
#endif

int main(int argc, char **argv) {
    const char *ws = getenv("ACADEMY_WORKSPACE");
    if (!ws || !ws[0]) {
        ws = ".";
    }
    execlp("python3", "python3", CHECK_SCRIPT, ws, (char *)NULL);
    perror("failed to start checker");
    return 1;
}
