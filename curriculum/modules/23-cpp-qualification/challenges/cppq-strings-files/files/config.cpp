#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>

std::string normalize(std::string value) {
    // TODO: lowercase letters and replace spaces with underscores.
    return value;
}

void save_config(const std::string& path, const std::map<std::string, std::string>& config) {
    // TODO: open path with std::ofstream, check it, and write key=value lines.
}

std::map<std::string, std::string> load_config(const std::string& path) {
    // TODO: open path with std::ifstream and parse non-empty key=value lines.
    return {};
}

int main() {
    const std::string path = "radio.conf";
    save_config(path, {{"station", normalize("Pi SDR Lab")}, {"token", "streams_keep_configs_offline"}});
    const auto config = load_config(path);
    const auto token = config.find("token");
    if (token != config.end() && config.at("station") == "pi_sdr_lab") {
        std::cout << token->second << '\n';
    }
}
