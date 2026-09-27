#include <iostream>
#include <memory>
int main() {
  // TODO: std::unique_ptr<int> p(new int(7));  or make_unique
  std::unique_ptr<int> p = std::make_unique<int>(7);
  std::cout << "owned=" << *p << "\n";
}
