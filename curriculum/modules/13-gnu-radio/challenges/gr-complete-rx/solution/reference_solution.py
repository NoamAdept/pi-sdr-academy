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

x=load_iq(); n=np.arange(len(x)); z=x*np.exp(-2j*np.pi*1500*n/12000); s=z.reshape(-1,8).mean(1); b=(s.real<0).astype(np.uint8); Path('answer.txt').write_text(np.packbits(b).tobytes().decode())
