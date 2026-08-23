# Explicit error contracts

Complete `errors.cpp` and run `./check`.

Use each mechanism for a distinct contract:
- `parse_hex_byte` throws `std::invalid_argument` when its input is not exactly two hexadecimal digits;
- `find_marker` returns `std::nullopt` when a marker is absent;
- `valid_checksum` is `[[nodiscard]]` and returns false for an expected mismatch.

Main must inspect the optional and status result before decoding. Do not use sentinel byte values or call `.value()` blindly.
