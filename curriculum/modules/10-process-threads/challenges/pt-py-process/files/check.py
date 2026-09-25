#!/usr/bin/env python3
"""Verify run_echo uses a real subprocess, not a parent-only return."""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path


def fail(message: str) -> None:
    print("Not yet:", message)
    raise SystemExit(1)


src = Path("worker.py").read_text(encoding="utf-8")
tree = ast.parse(src)
text = src.lower()
if "subprocess" not in text:
    fail("import and use the subprocess module")
if "notimplementederror" in text and "raise notimplementederror" in text:
    # still ok if they left a comment; check behavior below
    pass

import importlib.util

spec = importlib.util.spec_from_file_location("student", "worker.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

token = "child_token_7f3a"
got = mod.run_echo(token)
if got != token:
    fail(f"expected {token!r}, got {got!r}")

# Ensure they did not hardcode a trivial parent return without subprocess call sites
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
names = []
for n in calls:
    f = n.func
    if isinstance(f, ast.Attribute):
        names.append(f.attr)
    elif isinstance(f, ast.Name):
        names.append(f.id)
allowed = {"run", "check_output", "Popen", "call", "check_call"}
if not any(a in names for a in allowed):
    fail("call subprocess.run / check_output / Popen (a real child)")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
