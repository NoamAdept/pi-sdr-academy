#include <iostream>
int scale_const(const int& sample, int gain) {
  // TODO: return sample * gain (sample is const — do not assign to it)
  return 0;
}
int main() {
  int s = 3;
  std::cout << "scaled=" << scale_const(s, 2) << "\n";
}
