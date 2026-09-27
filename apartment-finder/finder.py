#!/usr/bin/env python3
"""Rerun the TAU rental search.

Example:
  python3 finder.py --output /path/to/apartment-candidates.md

Defaults: 2300–2600 ₪, TAU Ramat Aviv, 20 minutes by bike, drop women-only ads.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from apartment_finder.run import main

if __name__ == "__main__":
    raise SystemExit(main())
