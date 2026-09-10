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

x=np.load('input.npy'); fs=12000.0

y=np.load("output.npy")
if y.ndim!=1 or len(y)!=3000: fail("output.npy must contain 3000 samples")
if abs(np.mean(y))<.55: fail("selected channel is not centered/retained")
if np.std(y[100:])>.2: fail("unwanted channel remains after filtering and decimation")

print('CHECK_OK')
