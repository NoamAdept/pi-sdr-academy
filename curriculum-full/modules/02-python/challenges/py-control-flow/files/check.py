#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import importlib.util
spec = importlib.util.spec_from_file_location("student", "classify.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cases = {-3:"weak", 4:"weak", 5:"usable", 14:"usable", 15:"strong", 99:"strong"}
for value, expected in cases.items():
    if m.classify_signal(value) != expected:
        fail(f"classify_signal is wrong at boundary value {value}")
if m.summarize([1, 5, 14, 15, 20]) != {"weak":1, "usable":2, "strong":2}:
    fail("summarize must count every category")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
