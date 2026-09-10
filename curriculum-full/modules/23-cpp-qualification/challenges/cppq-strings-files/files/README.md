# Strings, files, and offline dependencies

Complete `config.cpp`, then run `./check`.

Normalize station names to lowercase with spaces replaced by underscores. Save and load `key=value` lines with `std::ofstream` and `std::ifstream`; reject files that cannot be opened.

This academy is offline. Do not add `vcpkg install`, `FetchContent`, or runtime downloads. If a future exercise needs a small third-party library, place its pinned source and license under `vendor/` and build it locally. CMake itself is covered in Module 6.
