#include <cstddef>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

unsigned char parse_hex_byte(const std::string& text) {
    // TODO: require exactly two hex digits; throw std::invalid_argument otherwise.
    return static_cast<unsigned char>(std::stoul(text, nullptr, 16));
}

std::optional<std::size_t> find_marker(
    const std::vector<unsigned char>& bytes, unsigned char marker) {
    // TODO: return the marker index, or std::nullopt when absent.
    return 0;
}

[[nodiscard]] bool valid_checksum(
    const std::vector<unsigned char>& payload, unsigned char expected) {
    // TODO: compare expected with the low eight bits of the payload sum.
    return false;
}

int main() {
    try {
        std::vector<unsigned char> packet;
        for (const auto* text : {"7e", "53", "41", "46", "45"}) {
            packet.push_back(parse_hex_byte(text));
        }

        const auto marker = find_marker(packet, 0x7e);
        // TODO: check marker before using it and validate payload checksum 0x1f.
        if (marker && false) {
            for (std::size_t i = *marker + 1; i < packet.size(); ++i) {
                std::cout << static_cast<char>(packet[i]);
            }
            std::cout << '\n';
        }
    } catch (const std::invalid_argument& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
