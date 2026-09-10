#!/usr/bin/env python3
import numpy as np
from pathlib import Path
Path('metadata.txt').write_text('sample_rate_hz=2000\nduration_seconds=1.0\n')
print("Generated tiny deterministic input data.")
