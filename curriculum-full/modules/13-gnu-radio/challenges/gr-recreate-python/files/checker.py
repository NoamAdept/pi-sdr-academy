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
ref=signal.lfilter(signal.firwin(101,1200,fs=12000),1,.25*x)[::2]
if y.shape!=ref.shape or not np.allclose(y,ref,rtol=2e-4,atol=2e-5): fail("output does not match the documented chain")

print('CHECK_OK')
