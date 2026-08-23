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

y = np.load("output.npy")
if y.shape != x.shape: fail("output.npy must have the same shape as input.npy")
def amp(z, f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/fs), z))/len(z)
if amp(y,350) < .55*amp(x,350): fail("350 Hz was attenuated too much")
if amp(y,3200) > .1*amp(x,3200): fail("3200 Hz needs at least 20 dB attenuation")

print('CHECK_OK')
