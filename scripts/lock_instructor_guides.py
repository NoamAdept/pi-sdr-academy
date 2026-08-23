#!/usr/bin/env python3
"""Lock instructor guides (encrypt + remove plaintext)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protect_instructor_guides import lock  # noqa: E402

if __name__ == "__main__":
    lock()
