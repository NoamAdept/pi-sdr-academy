#include <iostream>
#include <vector>
int main() {
  std::vector<int> gains{1, 2, 3};
  int sum = 0;
  // TODO: range-for over gains adding into sum
  for (int g : gains) {
    sum += g;
  }
  std::cout << "sum=" << sum << "\n";
}
