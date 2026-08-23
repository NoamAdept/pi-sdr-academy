#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import hashlib, subprocess, tempfile
script = Path("inventory.sh")
if "TODO" in script.read_text():
    fail("finish inventory.sh")
with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    samples = {"alpha.iq": b"abc", "space name.iq": b"\x00\x01radio", "ignore.txt": b"no"}
    for name, data in samples.items():
        (d / name).write_bytes(data)
    r = subprocess.run(["bash", str(script.resolve()), str(d)], text=True, capture_output=True)
    if r.returncode:
        fail("script failed: " + r.stderr.strip())
    expected = [f"{n},{len(v)},{hashlib.sha256(v).hexdigest()}" for n,v in sorted(samples.items()) if n.endswith(".iq")]
    p = Path("manifest.txt")
    if not p.exists() or p.read_text().splitlines() != expected:
        fail("manifest format, quoting, filtering, or sort order is incorrect")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
