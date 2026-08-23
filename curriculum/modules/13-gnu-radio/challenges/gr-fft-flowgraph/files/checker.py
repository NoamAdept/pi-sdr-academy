from pathlib import Path
import os
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

try: a=float(Path("answer.txt").read_text())
except Exception: fail("answer.txt must contain one number")
if abs(a-1375)>3: fail("the peak frequency is not correct")

print('CHECK_OK')
