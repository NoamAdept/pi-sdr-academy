#include <cstdio>
#include <cstdlib>
#include <sys/wait.h>
#include <unistd.h>

int main() {
  // TODO: fork(); child prints "child_ok" and exits 0;
  // parent waitpid's and prints "child_status=<exitcode>".
  return 2;
}
