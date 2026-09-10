#!/usr/bin/env python3
import os
from pathlib import Path

def fail(message):
    print("Not yet:", message)
    raise SystemExit(1)

from collections import Counter
counts = Counter()
for line in Path("receiver.log").read_text().splitlines():
    fields = dict(x.split("=", 1) for x in line.split() if "=" in x)
    if fields.get("level") == "WARN":
        counts[fields["component"]] += 1
expected = [f"{k}={counts[k]}" for k in sorted(counts)]
p = Path("report.txt")
if not p.exists():
    fail("create report.txt")
got = [x.strip() for x in p.read_text().splitlines() if x.strip()]
if got != expected:
    fail("count only WARN lines and use alphabetical component=count lines")

flag_path = Path(Path(".flagpath").read_text().strip()) if Path(".flagpath").exists() else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text('')
print('CHECK_OK')
