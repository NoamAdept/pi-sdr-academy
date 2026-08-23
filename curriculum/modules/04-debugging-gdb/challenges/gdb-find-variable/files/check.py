#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

p=Path("answer.txt")
if not p.exists(): fail("create answer.txt")
try: got=int(p.read_text().strip())
except ValueError: fail("write one decimal integer")
expected=10+3+7-2+9
if got!=expected: fail("inspect level at the fourth call, counting the first stop")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
