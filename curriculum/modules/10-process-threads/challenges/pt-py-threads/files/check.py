#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import os
from pathlib import Path


def fail(message: str) -> None:
    print("Not yet:", message)
    raise SystemExit(1)


src = Path("counter.py").read_text(encoding="utf-8")
if "threading" not in src:
    fail("import threading")
if "Lock" not in src:
    fail("protect the shared counter with a Lock")

tree = ast.parse(src)
attrs = [
    n.attr
    for n in ast.walk(tree)
    if isinstance(n, ast.Attribute)
]
if "Thread" not in attrs and "Thread" not in src:
    fail("create threading.Thread workers")

spec = importlib.util.spec_from_file_location("student", "counter.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

for threads, each in ((8, 5000), (4, 10000)):
    got = mod.parallel_add(threads, each)
    expect = threads * each
    if got != expect:
        fail(f"expected {expect}, got {got} (race or wrong math?)")

flag_path = (
    Path(Path(".flagpath").read_text().strip())
    if Path(".flagpath").exists()
    else Path(os.environ.get("ACADEMY_FLAG_PATH", "/home/flag.txt"))
)
flag_path.parent.mkdir(parents=True, exist_ok=True)
flag_path.write_text("")
print("CHECK_OK")
