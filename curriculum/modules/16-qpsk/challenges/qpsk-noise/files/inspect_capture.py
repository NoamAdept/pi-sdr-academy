from pathlib import Path
import os
import numpy as np
from scipy import signal

def load_iq(name="capture.iq"):
    a = np.fromfile(name, dtype="<f4").reshape(-1, 2)
    return a[:, 0] + 1j * a[:, 1]

def write_iq(name, x):
    np.column_stack((x.real, x.imag)).astype("<f4").tofile(name)

def flag_path():
    marker = Path(".flagpath")
    if marker.is_file():
        return Path(marker.read_text().strip())
    return Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))

x = load_iq()
print(f"capture.iq: {len(x)} complex samples ({8*len(x)} bytes)")
print(f"mean power: {np.mean(np.abs(x)**2):.4f}")
fs = 12000.0
spec = np.abs(np.fft.fftshift(np.fft.fft(x)))
freq = np.fft.fftshift(np.fft.fftfreq(len(x), 1/fs))
print(f"strongest FFT bin: {freq[np.argmax(spec)]:.1f} Hz")
print("symbol rate: 1500 symbols/s; samples/symbol: 8")
