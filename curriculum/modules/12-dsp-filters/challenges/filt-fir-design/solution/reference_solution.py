import numpy as np
from scipy import signal
np.save('taps.npy',signal.firwin(101,1300,fs=12000,window=('kaiser',5.0)))
