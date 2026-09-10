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

x=load_iq()
sps=8
s=x.reshape(-1,sps).mean(1)
bits=np.column_stack((s.imag<0,s.real<0)).astype(np.uint8).ravel()
Path('answer.txt').write_text(np.packbits(bits).tobytes().decode('ascii'))
