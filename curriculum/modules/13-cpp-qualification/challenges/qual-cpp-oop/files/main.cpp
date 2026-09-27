#include <iostream>
class Tone {
  int hz_;
public:
  explicit Tone(int hz) : hz_(hz) {}
  int freq() const {
    // TODO: return hz_
    return 0;
  }
};
int main() {
  Tone t(440);
  std::cout << "freq=" << t.freq() << "\n";
}
