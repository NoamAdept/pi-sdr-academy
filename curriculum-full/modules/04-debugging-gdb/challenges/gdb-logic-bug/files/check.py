#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

r=subprocess.run(["gcc","-std=c11","-Wall","-Wextra","-Werror","target.c","-o","target"],text=True,capture_output=True)
if r.returncode: fail("target.c must compile cleanly:\n"+r.stderr)
r=subprocess.run(["./target"],text=True,capture_output=True)
if r.returncode or r.stdout!="usable=4\n": fail("count values from 10 through 20 inclusive")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
