#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

r=subprocess.run(["gcc","-Wall","-Wextra","-Werror","-std=c11","meter.c","-o","meter"],text=True,capture_output=True)
if r.returncode: fail("meter.c must compile cleanly:\n"+r.stderr)
r=subprocess.run(["./meter"],text=True,capture_output=True)
if r.returncode or r.stdout != "average=20.0\n": fail("program must print exactly average=20.0")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
