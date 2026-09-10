#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace signal {
class ChannelPlan {
public:
 bool add(std::string name, std::uint64_t hz);
 std::vector<std::string> ordered_names() const;
private:
 struct Entry { std::string name; std::uint64_t hz; };
 std::vector<Entry> entries_;
};
}
