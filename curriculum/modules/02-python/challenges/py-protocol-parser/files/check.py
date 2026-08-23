#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import importlib.util
s=importlib.util.spec_from_file_location("student","protocol.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
def frame(p):
    c=0
    for b in p: c ^= b
    return b"\xaa\x55"+bytes([len(p)])+p+bytes([c])
good1=frame(b"OK"); bad=bytearray(frame(b"BAD")); bad[-1]^=1; good2=frame(bytes([0,255,16]))
stream=b"noise"+good1+b"xx"+bytes(bad)+b"z"+good2
if m.parse_frames(stream) != [b"OK", bytes([0,255,16])]:
    fail("find valid frames, reject bad checksum, and recover after noise")
if m.parse_frames(frame(b"A")[:-1]) != []:
    fail("an incomplete frame is not valid")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
