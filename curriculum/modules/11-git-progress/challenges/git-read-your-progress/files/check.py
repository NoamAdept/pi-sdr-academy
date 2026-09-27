#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path


def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)


uid = (os.environ.get("ACADEMY_USER") or "local").strip().lower()
uid = re.sub(r"[^a-z0-9_-]+", "-", uid).strip("-_") or "local"

# Prefer live progress file (always accurate), else peek helper.
data = Path(os.environ.get("ACADEMY_DATA", "")).expanduser()
live = data / "progress" / uid / "progress.json" if data.is_dir() else None
payload = None
if live and live.is_file():
    payload = json.loads(live.read_text(encoding="utf-8"))
else:
    proc = subprocess.run(["python3", "peek_progress"], capture_output=True, text=True)
    if proc.returncode != 0:
        fail(proc.stderr.strip() or "peek_progress failed — has the lab started once?")
    payload = json.loads(proc.stdout)

challenges = payload.get("challenges") or {}
cleared = sum(1 for c in challenges.values() if isinstance(c, dict) and c.get("solved"))

path = Path("cleared.txt")
if not path.is_file():
    fail("write cleared.txt with the number of solved challenges")
got = path.read_text(encoding="utf-8").strip().splitlines()[0].strip()
if got != str(cleared):
    fail(f"expected {cleared}, got {got!r}")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
print(f"Cleared on your branch: {cleared}")
