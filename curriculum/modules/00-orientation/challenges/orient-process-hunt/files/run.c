/*
 * ./run — starts a background helper. Source is removed after build.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static void die(const char *msg) {
    fprintf(stderr, "run failed: %s\n", msg);
    exit(1);
}

static int work_mode(void) {
    for (;;) sleep(30);
    return 0;
}

static void resolve_self(char *out, size_t out_sz, char *argv0) {
#if defined(__APPLE__)
    if (argv0 && argv0[0] == '/') {
        strncpy(out, argv0, out_sz - 1);
        out[out_sz - 1] = '\0';
        return;
    }
    if (argv0 && strchr(argv0, '/')) {
        if (getcwd(out, out_sz) == NULL) die("getcwd");
        size_t len = strlen(out);
        if (len + 1 + strlen(argv0) >= out_sz) die("path too long");
        out[len] = '/';
        memcpy(out + len + 1, argv0, strlen(argv0) + 1);
        return;
    }
#endif
    ssize_t n = readlink("/proc/self/exe", out, out_sz - 1);
    if (n > 0) {
        out[n] = '\0';
        return;
    }
    if (!argv0 || !argv0[0]) die("cannot resolve self");
    if (argv0[0] == '/') {
        strncpy(out, argv0, out_sz - 1);
        out[out_sz - 1] = '\0';
        return;
    }
    if (getcwd(out, out_sz) == NULL) die("getcwd");
    size_t len = strlen(out);
    if (len + 1 + strlen(argv0) >= out_sz) die("path too long");
    out[len] = '/';
    memcpy(out + len + 1, argv0, strlen(argv0) + 1);
}

int main(int argc, char **argv) {
    if (argc >= 2 && strcmp(argv[1], "--work") == 0) {
        return work_mode();
    }

    char base[512], note_path[576], code[64], self[4096];
    unsigned rnd;
    pid_t pid;

    int reap = system("pkill -f 'helper --work' >/dev/null 2>&1");
    (void)reap;
    usleep(150000);

    rnd = ((unsigned)time(NULL) ^ (unsigned)getpid() * 2654435761u);
    snprintf(base, sizeof(base), "/tmp/academy_note_%u", rnd % 100000000u);
    if (mkdir(base, 0700) != 0 && errno != EEXIST) die("mkdir");
    snprintf(note_path, sizeof(note_path), "%s/note.txt", base);
    snprintf(code, sizeof(code), "CODE-%08X", rnd);

    FILE *f = fopen(note_path, "w");
    if (!f) die("note");
    fprintf(
        f,
        "This is a small notes file created by the helper program.\n"
        "secret_code=%s\n",
        code
    );
    fclose(f);

    resolve_self(self, sizeof(self), argv[0]);
    pid = fork();
    if (pid < 0) die("fork");
    if (pid == 0) {
        if (setsid() < 0) _exit(1);
        int nullfd = open("/dev/null", O_RDWR);
        if (nullfd >= 0) {
            dup2(nullfd, 0);
            dup2(nullfd, 1);
            dup2(nullfd, 2);
            if (nullfd > 2) close(nullfd);
        }
        execl(self, "helper", "--work", "--notes", note_path, (char *)NULL);
        _exit(127);
    }

    printf("Helper program started in the background.\n");
    printf("It did not print a process number. Go find it.\n");
    return 0;
}
