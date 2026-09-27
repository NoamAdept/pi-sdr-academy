#include <iostream>
template <typename T>
T max_sample(T a, T b) {
  // TODO: return the larger of a and b
  return (a > b) ? a : b;
}
int main() {
  std::cout << "max=" << max_sample(3, 9) << "\n";
}
