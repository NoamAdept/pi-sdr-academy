from pathlib import Path
import os
import sys

def _expected():
    try:
        from academy.grading import expected_answer
        return expected_answer()
    except Exception as exc:
        print("Checker cannot load sealed answer:", exc)
        print("Re-run: academy start <challenge>   then: academy submit")
        raise SystemExit(1)

EXPECTED = _expected()

def fail(message):
    print("Not correct yet: " + message)
    raise SystemExit(1)

try:
    answer = Path("answer.txt").read_text().strip()
except OSError:
    fail("create answer.txt first")
if answer.lower() != EXPECTED.lower():
    fail("answer.txt does not contain the recovered answer")
print('CHECK_OK')

