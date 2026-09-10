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
if y.shape!=x.shape: fail("output.npy shape is wrong")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs),z))/len(z)
if amp(y,1500)/amp(x,1500)>10**(-25/20): fail("1500 Hz interferer remains")
for f in (700,2300):
    if amp(y,f)/amp(x,f)<10**(-3/20): fail(f"{f} Hz desired tone was damaged")

print('CHECK_OK')
