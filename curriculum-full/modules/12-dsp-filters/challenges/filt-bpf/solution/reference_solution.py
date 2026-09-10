import numpy as np
from scipy import signal
x=np.load('input.npy'); taps=signal.firwin(151,[1200,2400],pass_zero=False,fs=12000); np.save('output.npy',signal.lfilter(taps,1,x))
