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

x=load_iq(); y=load_iq("output.iq")
if len(y)!=len(x): fail("output.iq length differs from capture")
def amp(z,f): return abs(np.vdot(np.exp(2j*np.pi*f*np.arange(len(z))/12000),z))/len(z)
if amp(y,700)<.5*amp(x,700) or amp(y,3200)>.1*amp(x,3200): fail("filter response misses the target")

print('CHECK_OK')
