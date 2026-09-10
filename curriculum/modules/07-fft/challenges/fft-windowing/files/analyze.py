import numpy as np
x=np.load("signal.npy")
# TODO: compare rFFT power for x and x*np.hanning(len(x)).
# Exclude five bins on each side of each peak; write rect_far_power and hann_far_power.
