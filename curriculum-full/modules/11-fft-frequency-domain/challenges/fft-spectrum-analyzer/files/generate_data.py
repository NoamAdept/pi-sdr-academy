#!/usr/bin/env python3
import numpy as np
from pathlib import Path
rng=np.random.default_rng(11); n=np.arange(4096); x=np.sin(2*np.pi*140*n/2048)+.55*np.sin(2*np.pi*410*n/2048)+.01*rng.normal(size=n.size); np.save('signal.npy',x)
print("Generated tiny deterministic input data.")
