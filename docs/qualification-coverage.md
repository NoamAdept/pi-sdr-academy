# Qualification coverage map

Source materials (external):
- `qualification-main/python_qualification`
- `qualification-main/cpp_qualification`
- `qualification-main/GNURadio_Qualification`

Legend: **covered** in earlier modules · **new** in Modules 22–24.

## Python qualification → Module 22 (+ earlier Module 2)

| Qualification notebook | Academy coverage |
|------------------------|------------------|
| 01 Modules, packages, namespaces | **new** `pyq-modules-packages` |
| 02 Data types & dynamic typing | Module 2 `py-control-flow` + foundations |
| 03 OOP classes & objects | **new** `pyq-oop-classes` |
| 04 Immutability & state | **new** `pyq-modules-packages` / OOP + collections usage |
| 05 References & memory model | Taught alongside OOP/collections exercises |
| 06 Modern Python features | **new** `pyq-modern-python` |
| 07 Collections & comprehensions | **new** `pyq-collections` |
| 08 Context managers | **new** `pyq-context-exceptions` |
| 09 Errors & exceptions | **new** `pyq-context-exceptions` (+ `py-file-parser`) |
| 10 Project structure & packaging | **new** `pyq-modules-packages` (offline layout; no pip) |
| 11 Bit manipulation & struct | Module 2 `py-binary-decoder` + **new** `pyq-bits-serialize` |
| 12 Dataclasses & serialization | **new** `pyq-bits-serialize` |
| 13 Performance & decorators | **new** `pyq-modern-python` |
| 14 Type hinting & generics | **new** `pyq-modern-python` |

## C++ qualification → Module 23 (+ Modules 3–6, 8)

| Qualification notebook | Academy coverage |
|------------------------|------------------|
| 01 Namespaces & scope | **new** `cppq-namespaces-const` |
| 02 Strings & files | **new** `cppq-strings-files` |
| 03 OOP & design patterns | Module 5 `cpp-first-class` + patterns in Module 23 starters |
| 04 const & volatile | **new** `cppq-namespaces-const` |
| 05 Pointers & references | Module 3 C + Module 5 C++ |
| 06 Modern C++ | **new** `cppq-modern-cpp` |
| 07 STL | Module 5 `cpp-stl` |
| 08 RAII & smart pointers | Module 5 `cpp-raii`, `cpp-smart-ptr` |
| 09 Error handling & safety | **new** `cppq-errors-optional` |
| 10 CMake | Module 6 |
| 11 Package management (vcpkg) | **adapted offline** notes in Module 23 (vendor locally; no network) |
| 12 Low-level data manipulation | **new** `cppq-lowlevel-concurrency` (+ `c-memory-layout`) |
| 13 Templates | **new** `cppq-templates` |
| 14 Concurrency & networking | Module 8 + **new** `cppq-lowlevel-concurrency` |
| 15 ISR integration | **new** `cppq-lowlevel-concurrency` (simulated `extern "C"` / `volatile`) |

## GNU Radio qualification → Module 24 (+ Module 13)

| Qualification notebook | Academy coverage |
|------------------------|------------------|
| 01 Intro GNU Radio C++ API | **new** `grq-cpp-blocks` |
| 02 Flowgraphs & connections | **new** `grq-flowgraph-connect` (+ Module 13) |
| 03 Data flow & vector blocks | **new** `grq-vector-dataflow`, `grq-tags-messages` |
| 04 Signal processing project | **new** `grq-signal-chain`, `grq-complete-topblock` |

All Module 24 challenges run **offline with a NumPy/Python flowgraph simulator** if GNU Radio is not installed.

## Offline constraint

Anything that assumed online `vcpkg` / `pip install` in the qualification notebooks is rewritten here as local/vendored-only workflows.
