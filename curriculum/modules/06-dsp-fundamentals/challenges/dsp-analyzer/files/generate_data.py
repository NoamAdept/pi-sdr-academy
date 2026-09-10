#!/usr/bin/env python3
import numpy as np
from pathlib import Path
rng=np.random.default_rng(7); n=np.arange(4096); np.save('signal.npy',.8*np.sin(2*np.pi*180*n/2048)+.01*rng.normal(size=n.size))
print("Generated tiny deterministic input data.")
