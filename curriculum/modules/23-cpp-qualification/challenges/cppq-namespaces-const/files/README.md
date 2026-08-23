# Qualified names and const

Complete every `TODO` in `qualification.cpp`.

Requirements:
- define separate `radio::channel()` and `diagnostics::channel()` functions;
- use `::` qualification when calling both;
- make the receiver getter const-correct;
- read the supplied volatile readiness flag, but do not claim it is thread-safe.

Run `./check`. The checker compiles with C++17 warnings-as-errors and writes the flag only after the program prints `145`.
