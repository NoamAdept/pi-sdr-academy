#include <iostream>
#include <thread>
int main() {
  int ready = 0;
  std::thread t([&]() { ready = 1; });
  // TODO: join the thread before reading ready
  t.join();
  std::cout << "ready=" << ready << "\n";
}
