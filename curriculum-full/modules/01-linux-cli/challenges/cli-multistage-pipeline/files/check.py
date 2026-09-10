#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

import csv
from collections import defaultdict
vals = defaultdict(list)
for r in csv.DictReader(Path("signals.csv").open()):
    if r["status"] == "LOCKED" and float(r["snr"]) >= 10:
        vals[r["band"]].append(float(r["snr"]))
expected = [f"{b},{len(vals[b])},{sum(vals[b])/len(vals[b]):.1f}" for b in sorted(vals)]
p = Path("summary.csv")
if not p.exists() or p.read_text().splitlines() != expected:
    fail("summary.csv does not match the requested filtering, grouping, and formatting")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
