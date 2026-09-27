#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess
from pathlib import Path

def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)

try:
    subprocess.run(["g++","-std=c++17","-Wall","-Wextra","-O0","-pthread","-o","prog","main.cpp"],
                   check=True, capture_output=True, text=True)
except FileNotFoundError:
    fail("c++ not found")
except subprocess.CalledProcessError as e:
    fail(e.stderr.strip() or "compile failed")
out = subprocess.check_output(["./prog"], text=True, timeout=5)
if 'tune=146.52' not in out: fail("missing "+'tune=146.52')
src = Path("main.cpp").read_text(encoding="utf-8")
assert "getline" in src

fp = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH","/home/flag.txt"))
fp.parent.mkdir(parents=True, exist_ok=True)
fp.write_text("")
print("CHECK_OK")
