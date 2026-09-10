#!/usr/bin/env python3
import numpy as np
from pathlib import Path
n=np.arange(2048); np.save('signal.npy',np.sin(2*np.pi*900*n/1000))
print("Generated tiny deterministic input data.")
