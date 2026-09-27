#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path


def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)


uid = (os.environ.get("ACADEMY_USER") or "local").strip().lower()
uid = re.sub(r"[^a-z0-9_-]+", "-", uid).strip("-_") or "local"
expect = f"progress/{uid}"

path = Path("answer.txt")
if not path.is_file():
    fail("create answer.txt with your branch name (run ./whoami_branch)")
got = path.read_text(encoding="utf-8").strip().splitlines()[0].strip()
if got != expect:
    fail(f"expected {expect!r}, got {got!r}")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
print(f"Your branch is {expect} — the lab keeps it updated for you.")
