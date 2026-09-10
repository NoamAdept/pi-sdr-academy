#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import importlib.util, subprocess, tempfile
s = importlib.util.spec_from_file_location("student", "parse_config.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
expected = {"frequency":"145800000", "mode":"FM", "label":"roof=antenna", "gain":"18"}
if m.parse_config("receiver.conf") != expected:
    fail("parser did not handle comments, spaces, or an equals sign in a value")
with tempfile.NamedTemporaryFile("w", delete=False) as f:
    f.write("good=1\nbroken line\n"); bad = f.name
try:
    try: m.parse_config(bad)
    except ValueError: pass
    else: fail("raise ValueError for a non-comment line without =")
finally:
    Path(bad).unlink()
r = subprocess.run(["python3", "parse_config.py", "receiver.conf"])
if r.returncode or not Path("parsed.txt").exists():
    fail("command-line program must create parsed.txt")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
