#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

p=Path("answer.txt")
if not p.exists(): fail("create answer.txt")
expected=bytes([0xaa,0x55,3,0x10,0,0xfe,1,0xef]).hex(" ")
if p.read_text().strip().lower()!=expected: fail("use x/8bx packet and normalize all eight bytes")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
