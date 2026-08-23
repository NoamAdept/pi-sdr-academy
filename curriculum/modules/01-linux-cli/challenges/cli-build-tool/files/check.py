#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import subprocess
mk = Path("Makefile").read_text()
if "TODO" in mk or "signal.h" not in mk:
    fail("complete the Makefile and include header dependencies")
subprocess.run(["make", "clean"], capture_output=True)
r = subprocess.run(["make"], text=True, capture_output=True)
if r.returncode or not Path("analyzer").exists():
    fail("make did not build analyzer: " + r.stderr.strip())
r = subprocess.run(["./analyzer"], text=True, capture_output=True)
if r.returncode or r.stdout.strip() != "average=15":
    fail("analyzer output is not average=15")
r = subprocess.run(["make", "clean"], text=True, capture_output=True)
if r.returncode or Path("analyzer").exists() or list(Path(".").glob("*.o")):
    fail("make clean must remove analyzer and object files")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
