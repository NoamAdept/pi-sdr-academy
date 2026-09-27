#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, os
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location("student", "radio_math.py")
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)
assert abs(m.wavelength_m(100.0)-299792458/100e6)<1e-6
assert "math" in Path("radio_math.py").read_text()

fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
