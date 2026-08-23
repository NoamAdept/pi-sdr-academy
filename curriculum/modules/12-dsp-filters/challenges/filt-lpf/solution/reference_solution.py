import numpy as np
from scipy import signal
x=np.load('input.npy'); taps=signal.firwin(101,1000,fs=12000); np.save('output.npy',signal.lfilter(taps,1,x))
