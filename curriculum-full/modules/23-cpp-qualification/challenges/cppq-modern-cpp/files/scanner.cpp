#include <array>
#include <iostream>

enum class Signal {
    quiet,
    weak,
    strong,
};

constexpr Signal classify(int level) {
    // TODO: below 10 is quiet, 10..49 is weak, and 50 or more is strong.
    return Signal::quiet;
}

static_assert(classify(75) == Signal::strong, "classifier must work at compile time");

int main() {
    // TODO: use std::array for 3, 12, 55, 80, 49.
    const int levels[] = {3, 12, 55, 80, 49};
    int strong_count = 0;

    // TODO: replace this indexed loop with a range-for and use auto.
    for (int index = 0; index < 5; ++index) {
        if (classify(levels[index]) == Signal::strong) {
            ++strong_count;
        }
    }
    std::cout << strong_count << '\n';
}
