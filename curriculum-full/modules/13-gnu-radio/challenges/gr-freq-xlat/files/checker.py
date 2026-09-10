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

y=load_iq("output.iq")
if len(y)!=12000: fail("output length is wrong")
phase_step=np.angle(np.mean(y[1:]*np.conj(y[:-1])))
if abs(phase_step*12000/(2*np.pi))>5 or abs(np.mean(y))<.8: fail("channel is not centered at DC")

print('CHECK_OK')
