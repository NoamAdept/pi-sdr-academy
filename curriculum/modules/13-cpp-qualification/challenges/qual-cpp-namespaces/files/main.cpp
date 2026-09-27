#include <iostream>
namespace RadioMath {
  int add(int a, int b) { return a + b; }
  int sub(int a, int b) {
    // TODO: return a - b
    return 0;
  }
}
int main() {
  std::cout << "sum=" << RadioMath::add(10, 5) << "\n";
  std::cout << "diff=" << RadioMath::sub(10, 5) << "\n";
}
