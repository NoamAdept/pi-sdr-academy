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

x=np.load("input.npy"); y=np.load("output.npy")
if y.shape!=x.shape or not np.allclose(y,.5*x,rtol=1e-5,atol=1e-6): fail("output does not match a gain of 0.5")

print('CHECK_OK')
