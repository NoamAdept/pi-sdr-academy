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

try: p=[v.strip().lower() for v in Path("answer.txt").read_text().split(",")]
except Exception: fail("missing answer.txt")
if len(p)!=3 or p[2]!="qpsk": fail("format is sample_rate,carrier,modulation")
try: fs,fc=float(p[0]),float(p[1])
except ValueError: fail("sample rate and carrier must be numbers")
if abs(fs-12000)>1 or abs(fc-900)>10: fail("one or more estimated parameters is wrong")

print('CHECK_OK')
