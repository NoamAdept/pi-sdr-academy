#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

p=Path("answer.txt")
if not p.exists(): fail("write the inspected decimal value to answer.txt")
expected=(17<<2)+5
try: got=int(p.read_text().strip(),10)
except ValueError: fail("answer.txt must contain one decimal integer")
if got!=expected: fail("break at checkpoint and print its sample argument")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
