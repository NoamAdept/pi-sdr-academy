from pathlib import Path
import numpy as np
p=Path("capture.iq")
if p.exists():
    a=np.fromfile(p,dtype="<f4").reshape(-1,2); x=a[:,0]+1j*a[:,1]
    print("complex samples:",len(x),"mean power:",float(np.mean(abs(x)**2)))
    f=np.fft.fftshift(np.fft.fftfreq(len(x))); peak=f[np.argmax(abs(np.fft.fftshift(np.fft.fft(x))))]
    print("strongest FFT bin (cycles/sample):",float(peak))
elif Path("capture.bits").exists():
    b=''.join(Path("capture.bits").read_text().split()); print("bits:",len(b),"first 64:",b[:64])
else:
    z=np.load("pulse_data.npz"); print("arrays:",", ".join(f"{k}{z[k].shape}" for k in z.files))
