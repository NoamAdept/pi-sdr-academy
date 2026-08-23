import numpy as np
from scipy import signal
x=np.load('input.npy'); n=np.arange(len(x)); z=x*np.exp(-2j*np.pi*2400*n/12000); taps=signal.firwin(129,500,fs=12000); np.save('output.npy',signal.lfilter(taps,1,z)[::4])
