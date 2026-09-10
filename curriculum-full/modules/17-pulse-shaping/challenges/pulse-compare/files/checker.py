from pathlib import Path
import os

EXPECTED = 'rrc'

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
