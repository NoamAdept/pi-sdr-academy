#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def fail(msg: str) -> None:
    print("Not yet:", msg)
    raise SystemExit(1)


uid = (os.environ.get("ACADEMY_USER") or "local").strip().lower()
uid = re.sub(r"[^a-z0-9_-]+", "-", uid).strip("-_") or "local"
branch = f"progress/{uid}"

marker = Path("UPLOAD_OK")
practice = Path("practice-remote.git")
if not marker.is_file() or not practice.is_dir():
    fail("run ./practice_upload first (creates practice-remote.git)")

show = subprocess.run(
    ["git", "-C", str(practice), "show", f"{branch}:progress.json"],
    capture_output=True,
    text=True,
)
if show.returncode != 0:
    fail(f"{branch} not found on practice-remote.git — re-run ./practice_upload")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
print("Practice upload verified. Real world: academy progress remote <url> && academy progress push")
