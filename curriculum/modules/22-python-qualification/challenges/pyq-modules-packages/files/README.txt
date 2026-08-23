REPAIR THE RECEIVER PACKAGE

The package should classify three received power readings.

1. Run: python3 analyze.py
2. Fix the two import lines marked YOUR CODE HERE.
3. Run: ./check

Expected report:
  -35 dBm: excellent
  -67 dBm: usable
  -92 dBm: weak

Layout:
  analyze.py                 application / entry point
  radio_tools/__init__.py    package initializer and public API
  radio_tools/levels.py      package module

A virtual environment (`python3 -m venv .venv`) isolates third-party packages
for a project. This exercise uses only local code and the standard library, so
do not create a venv and do not install anything.
