#include <algorithm>
#include <iostream>
#include <vector>
int main() {
  std::vector<int> v{1, 9, 3, 7};
  // TODO: auto it = std::max_element(v.begin(), v.end());
  auto it = std::max_element(v.begin(), v.end());
  std::cout << "peak=" << *it << "\n";
}
