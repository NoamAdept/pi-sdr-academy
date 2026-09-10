#include <array>
#include <cstdint>
#include <iostream>
#include <thread>

#pragma pack(push, 1)
struct WirePacket {
    std::uint8_t header;
    std::array<std::uint8_t, 2> sequence_be;
    std::array<std::uint8_t, 4> payload;
};
#pragma pack(pop)

static_assert(sizeof(WirePacket) == 7, "wire layout changed");

WirePacket shared_packet{};
volatile bool packet_ready = false;  // TODO: replace with std::atomic<bool>.

extern "C" void simulated_isr(const WirePacket* incoming) {
    // TODO: protect the shared copy with std::mutex.
    shared_packet = *incoming;
    // TODO: publish readiness with a release-store.
    packet_ready = true;
}

std::uint8_t mode(const WirePacket& packet) {
    // TODO: extract the low three header bits with a mask.
    return packet.header;
}

std::uint16_t sequence(const WirePacket& packet) {
    // TODO: decode the two-byte big-endian value with shifts and OR.
    return packet.sequence_be[0];
}

int main() {
    const WirePacket incoming{0b10101101, {0x12, 0x34}, {'L', 'O', 'C', 'K'}};
    std::thread producer([&incoming] { simulated_isr(&incoming); });

    // TODO: wait with an acquire-load, lock, and copy shared_packet locally.
    while (!packet_ready) {
        std::this_thread::yield();
    }
    const WirePacket local = shared_packet;
    producer.join();

    for (const auto byte : local.payload) {
        std::cout << static_cast<char>(byte);
    }
    std::cout << ':' << static_cast<unsigned>(mode(local))
              << ':' << sequence(local) << '\n';
}
