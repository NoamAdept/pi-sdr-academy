#include <cstdint>
#include <iostream>
int main() {
  uint16_t id = 0xABCD;
  uint8_t hi = static_cast<uint8_t>((id >> 8) & 0xFF);
  uint8_t lo = static_cast<uint8_t>(id & 0xFF);
  std::cout << std::hex << "hex=" << int(hi) << int(lo) << "\n";
}
