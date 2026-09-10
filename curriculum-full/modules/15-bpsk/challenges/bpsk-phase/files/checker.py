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

import numpy as np
from scipy import signal

def load_iq(name="capture.iq"):
    a = np.fromfile(name, dtype="<f4").reshape(-1, 2)
    return a[:, 0] + 1j * a[:, 1]

def write_iq(name, x):
    np.column_stack((x.real, x.imag)).astype("<f4").tofile(name)


def fail(message):
    print('Not correct yet: ' + message)
    raise SystemExit(1)

try: a=Path("answer.txt").read_text().strip()
except Exception: fail("missing answer.txt")
if a != _expected(): fail('decoded text is not the transmitted flag')

print('CHECK_OK')
