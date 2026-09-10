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
# Fourth-power phase has a 90-degree ambiguity; known ASCII resolves it.
raw=np.angle(np.mean(s**4))/4-np.pi/4
text=None
for k in range(4):
    r=s*np.exp(-1j*(raw+k*np.pi/2))
    bits=np.column_stack((r.imag<0,r.real<0)).astype(np.uint8).ravel()
    candidate=np.packbits(bits).tobytes().decode('ascii',errors='ignore')
    if candidate.startswith('flag{'): text=candidate; break
if text is None: raise RuntimeError('could not resolve QPSK quadrant ambiguity')
Path('answer.txt').write_text(text)
raise SystemExit(0)
Path('answer.txt').write_text(np.packbits(bits).tobytes().decode('ascii'))
