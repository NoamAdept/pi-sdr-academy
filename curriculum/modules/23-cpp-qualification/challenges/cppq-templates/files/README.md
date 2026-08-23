# Generic clamp and ring buffer

Complete the templates in `templates.cpp`, then run `./check`.

`clamp_value` must work for comparable types and include both bounds. `RingBuffer<T, N>` must:
- reject zero capacity at compile time;
- retain at most `N` values;
- overwrite the oldest value when full;
- expose `size()` and checked `at(index)` in oldest-to-newest order.

The decoder clamps raw integers to byte range, stores the newest eight bytes, and prints `TEMPLATE`.
