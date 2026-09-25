#include <cstdio>
#include <mutex>
#include <thread>
#include <vector>

// Return n_threads * per_thread using real std::thread workers + a mutex.
long long parallel_add(int n_threads, int per_thread) {
  // TODO: spawn threads; protect a shared total with std::mutex; join all.
  (void)n_threads;
  (void)per_thread;
  return -1;
}

int main() {
  long long got = parallel_add(4, 1000);
  std::printf("%lld\n", got);
  return got == 4000 ? 0 : 1;
}
