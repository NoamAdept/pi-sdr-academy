#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import importlib.util, struct, subprocess, tempfile
sample_rows = [(145800000,-42,1),(433500000,-71,0),(28120000,-19,2)]
Path("samples.bin").write_bytes(b"".join(struct.pack("<IhB", *r) for r in sample_rows))
s=importlib.util.spec_from_file_location("student","decode.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
if m.decode_records("samples.bin") != sample_rows:
    fail("decoded tuples do not match the documented record layout")
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b"123"); bad=f.name
try:
    try: m.decode_records(bad)
    except ValueError: pass
    else: fail("reject an incomplete final record with ValueError")
finally: Path(bad).unlink()
if subprocess.run(["python3","decode.py","samples.bin"]).returncode or not Path("decoded.csv").exists():
    fail("command-line program must create decoded.csv")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
