#!/usr/bin/env python3
import numpy as np
from pathlib import Path
n=np.arange(1024); np.save('signal.npy',np.sin(2*np.pi*123.4*n/1024))
print("Generated tiny deterministic input data.")
