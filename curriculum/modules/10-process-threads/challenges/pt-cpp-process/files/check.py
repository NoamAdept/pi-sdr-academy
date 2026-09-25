#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def fail(message: str) -> None:
    print("Not yet:", message)
    raise SystemExit(1)


src = Path("controller.cpp").read_text(encoding="utf-8")
if "fork" not in src:
    fail("call fork()")
if "wait" not in src:
    fail("wait for the child (waitpid / wait)")

try:
    subprocess.run(
        ["c++", "-Wall", "-Wextra", "-O0", "-o", "controller", "controller.cpp"],
        check=True,
        capture_output=True,
        text=True,
    )
except FileNotFoundError:
    fail("c++ compiler not found on PATH")
except subprocess.CalledProcessError as exc:
    fail(exc.stderr.strip() or "compile failed")

try:
    out = subprocess.check_output(["./controller"], text=True, timeout=3)
except Exception as exc:  # noqa: BLE001
    fail(str(exc))

if "child_ok" not in out:
    fail("child should print child_ok")
if "child_status=0" not in out:
    fail("parent should print child_status=0")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
