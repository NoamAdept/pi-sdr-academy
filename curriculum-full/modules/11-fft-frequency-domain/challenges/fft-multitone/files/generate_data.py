#!/usr/bin/env python3
import numpy as np
from pathlib import Path
n=np.arange(2048); x=sum(a*np.sin(2*np.pi*f*n/2048) for a,f in [(1,80),(.7,205),(.5,333)]); np.save('signal.npy',x)
print("Generated tiny deterministic input data.")
