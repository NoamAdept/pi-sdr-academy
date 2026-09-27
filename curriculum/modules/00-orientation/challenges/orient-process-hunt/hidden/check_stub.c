/*
 * Tiny wrapper — runs the hidden checker. Source removed after build.
 * setup.sh compiles with: cc -include /path/to/check_script.h -o check check_stub.c
 * where check_script.h defines CHECK_SCRIPT as the absolute path to check.py.
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef CHECK_SCRIPT
#error "CHECK_SCRIPT must be defined at compile time (via -include check_script.h)"
#endif

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;
    const char *ws = getenv("ACADEMY_WORKSPACE");
    if (!ws || !ws[0]) {
        ws = ".";
    }
    execlp("python3", "python3", CHECK_SCRIPT, ws, (char *)NULL);
    perror("failed to start checker");
    return 1;
}
