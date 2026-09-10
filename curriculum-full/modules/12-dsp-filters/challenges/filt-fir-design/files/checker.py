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

t=np.load("taps.npy")
if t.ndim!=1 or not 41<=len(t)<=161 or np.max(np.abs(np.imag(t)))>1e-8: fail("use 41..161 real taps")
w,h=signal.freqz(np.real(t),worN=8192,fs=fs)
pb=np.abs(h[w<=900]); sb=np.abs(h[w>=1800])
if pb.min()<10**(-3/20) or pb.max()>10**(3/20): fail("passband must stay within 3 dB")
if sb.max()>10**(-25/20): fail("stopband needs 25 dB attenuation")

print('CHECK_OK')
