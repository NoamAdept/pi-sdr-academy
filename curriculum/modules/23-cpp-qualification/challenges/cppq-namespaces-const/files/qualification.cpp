#include <iostream>

namespace radio {
int channel() {
    return 144;
}
}  // namespace radio

namespace diagnostics {
int channel() {
    return 1;
}
}  // namespace diagnostics

class Receiver {
public:
    explicit Receiver(int frequency) : frequency_(frequency) {}

    // TODO: make this member function callable on a const Receiver.
    int frequency() {
        return frequency_;
    }

private:
    int frequency_;
};

volatile int interrupt_ready = 1;

bool shared_ready() {
    // TODO: explicitly read interrupt_ready and return whether it is nonzero.
    return false;
}

int main() {
    const Receiver receiver{145};
    // TODO: use qualified namespace calls and verify 144 + 1 equals the receiver value.
    if (shared_ready() && false) {
        std::cout << receiver.frequency() << '\n';
    }
}
