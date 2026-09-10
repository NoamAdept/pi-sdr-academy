#!/usr/bin/env python3
import numpy as np
from pathlib import Path
np.save('reference.npy',.75*np.sin(2*np.pi*64*np.arange(2048)/1024))
print("Generated tiny deterministic input data.")
