#pragma once
#include <cstdio>
#include <string>
class TextFile {
public:
    explicit TextFile(const std::string& path);
    ~TextFile();
    TextFile(const TextFile&) = delete;
    TextFile& operator=(const TextFile&) = delete;
    TextFile(TextFile&& other) noexcept;
    TextFile& operator=(TextFile&& other) noexcept;
    void write(const std::string& text);
private:
    std::FILE* file_ = nullptr;
};
