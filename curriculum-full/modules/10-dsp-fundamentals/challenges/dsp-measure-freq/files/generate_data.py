#!/usr/bin/env python3
import numpy as np
from pathlib import Path
n=np.arange(2048); np.save('signal.npy',.8*np.sin(2*np.pi*73*n/1024))
print("Generated tiny deterministic input data.")
