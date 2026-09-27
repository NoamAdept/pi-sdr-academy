#include <iostream>
#include <stdexcept>
int apply_gain(int sample, int gain) {
  if (gain < 0) throw std::invalid_argument("gain");
  return sample * gain;
}
int main() {
  try {
    int v = apply_gain(4, 2);
    std::cout << "ok=" << v << "\n";
    apply_gain(1, -1);
    std::cout << "should_not_print\n";
  } catch (const std::invalid_argument&) {
    std::cout << "caught\n";
  }
}
