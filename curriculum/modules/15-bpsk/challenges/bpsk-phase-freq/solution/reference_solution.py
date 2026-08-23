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
# The 2th power removes data modulation; its phase slope reveals CFO.
p=np.unwrap(np.angle(x**2))
cfo=np.polyfit(np.arange(len(x)),p,1)[0]*12000/(2*np.pi*2)
x=x*np.exp(-2j*np.pi*cfo*np.arange(len(x))/12000)
s=x.reshape(-1,sps).mean(1)
phi=np.angle(np.mean(s**2))/2
s=s*np.exp(-1j*phi)
bits=(s.real<0).astype(np.uint8)
Path('answer.txt').write_text(np.packbits(bits).tobytes().decode('ascii'))
