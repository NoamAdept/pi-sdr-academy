#include <fstream>
#include <iostream>
#include <string>
int main() {
  std::ifstream in("tune.txt");
  std::string line;
  if (!std::getline(in, line)) return 1;
  // TODO: already reading — ensure output format tune=<line>
  std::cout << "tune=" << line << "\n";
}
