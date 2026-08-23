#!/usr/bin/env python3
import os, subprocess, tempfile
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

p=Path("answer.txt")
if not p.exists(): fail("create answer.txt from the backtrace")
parts=[x.strip() for x in p.read_text().strip().split("->")]
if parts!=["main","receive","demodulate","capture"]: fail("list every stack function from outermost to innermost")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
