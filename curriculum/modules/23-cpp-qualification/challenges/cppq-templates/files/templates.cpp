#include <array>
#include <cstddef>
#include <iostream>
#include <stdexcept>

template <typename T>
constexpr T clamp_value(const T& value, const T& low, const T& high) {
    // TODO: clamp value inclusively to [low, high].
    return value;
}

template <typename T, std::size_t N>
class RingBuffer {
    static_assert(N > 0, "RingBuffer capacity must be positive");

public:
    void push(const T& value) {
        // TODO: append, or overwrite and advance the oldest index when full.
    }

    std::size_t size() const {
        // TODO
        return 0;
    }

    const T& at(std::size_t index) const {
        // TODO: throw std::out_of_range if index >= size_.
        return data_.at(index);
    }

private:
    std::array<T, N> data_{};
    std::size_t oldest_ = 0;
    std::size_t size_ = 0;
};

int main() {
    RingBuffer<int, 8> decoded;
    for (const auto raw : std::array<int, 9>{88, 84, 69, 77, 80, 76, 65, 84, 69}) {
        decoded.push(clamp_value(raw, 0, 255));
    }
    for (std::size_t i = 0; i < decoded.size(); ++i) {
        std::cout << static_cast<char>(decoded.at(i));
    }
    std::cout << '\n';
}
