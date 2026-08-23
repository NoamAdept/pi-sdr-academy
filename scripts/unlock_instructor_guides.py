#!/usr/bin/env python3
"""Unlock instructor guides (decrypt with password)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protect_instructor_guides import unlock  # noqa: E402

if __name__ == "__main__":
    unlock()
