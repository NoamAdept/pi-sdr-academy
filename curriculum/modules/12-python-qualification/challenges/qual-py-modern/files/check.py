#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, os
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location("student", "tune.py")
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)
assert m.format_tune(146.52,"NFM")=="tune NFM @ 146.520 MHz"

fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
