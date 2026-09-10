#!/usr/bin/env python3
import numpy as np
from pathlib import Path
n=np.arange(2048); x=np.sin(2*np.pi*12*n/1024); np.save('truth.npy',x); x[1::4]=np.nan; np.save('sparse.npy',x)
print("Generated tiny deterministic input data.")
