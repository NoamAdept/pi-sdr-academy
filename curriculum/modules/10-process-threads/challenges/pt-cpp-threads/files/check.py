#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def fail(message: str) -> None:
    print("Not yet:", message)
    raise SystemExit(1)


src = Path("workers.cpp").read_text(encoding="utf-8")
if "thread" not in src:
    fail("use std::thread")
if "mutex" not in src.lower():
    fail("protect the shared total with std::mutex")
if "join" not in src:
    fail("join every thread before returning")
if "parallel_add" not in src:
    fail("implement parallel_add")

try:
    subprocess.run(
        [
            "c++",
            "-Wall",
            "-Wextra",
            "-O0",
            "-pthread",
            "-std=c++17",
            "-o",
            "workers",
            "workers.cpp",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
except FileNotFoundError:
    fail("c++ compiler not found on PATH")
except subprocess.CalledProcessError as exc:
    fail(exc.stderr.strip() or "compile failed")

try:
    out = subprocess.check_output(["./workers"], text=True, timeout=5)
except Exception as exc:  # noqa: BLE001
    fail(str(exc))

if out.strip() != "4000":
    fail(f"expected printed total 4000, got {out!r}")

# Reject obvious hardcodes that skip spawning work.
if "return 4000" in src.replace(" ", "") or "return4000" in src.replace(" ", ""):
    fail("compute the total with threads — do not hardcode 4000")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
