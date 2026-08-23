# Low-level packet and callback boundary

Repair `receiver.cpp`, then run `./check`.

The packed wire packet contains:
- one header byte: low 3 bits are mode, upper 5 bits are flags;
- a two-byte big-endian sequence number;
- four payload bytes.

Keep `extern "C"` on the simulated ISR callback. Replace the volatile readiness flag with `std::atomic<bool>`, protect shared packet copying with `std::mutex`, and use release/acquire publication. Decode fields with unsigned masks and shifts. The expected diagnostic is `LOCK:5:4660`.

The callback is only an ISR simulation: a real interrupt handler usually cannot lock a mutex or call general C++ runtime facilities.
