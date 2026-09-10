import numpy as np
from scipy import signal
x=np.load('input.npy'); b,a=signal.iirnotch(1500,30,fs=12000); np.save('output.npy',signal.lfilter(b,a,x))
