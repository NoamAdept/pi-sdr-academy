#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, os
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location("student", "tone_chain.py")
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)
assert m.process_tone([1.0,-3.0,0.5])==[2.0,6.0,1.0]

fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
