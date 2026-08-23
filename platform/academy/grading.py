"""Helpers for challenge ./check scripts — award the sealed session flag."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .paths import resolve_flag_path, write_flag_file
from .secrets import load_session_answer, load_session_flag


def workspace_root(explicit: str | Path | None = None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("ACADEMY_WORKSPACE")
    if env:
        return Path(env).resolve()
    return Path.cwd().resolve()


def current_challenge_id(workspace: Path | None = None) -> str:
    root = workspace or workspace_root()
    marker = root / ".challenge"
    if not marker.is_file():
        raise RuntimeError(
            "No .challenge file — run: next"
        )
    cid = marker.read_text(encoding="utf-8").strip()
    if not cid:
        raise RuntimeError("Empty .challenge file")
    return cid


def data_dir() -> Path:
    return Path(os.environ.get("ACADEMY_DATA", str(Path.home() / ".academy")))


def expected_answer(workspace: str | Path | None = None) -> str:
    """
    Value students recover into answer.txt (from sealed store).
    Checkers must call this — never hardcode flag{...}.
    """
    root = workspace_root(workspace)
    cid = current_challenge_id(root)
    answer = load_session_answer(data_dir(), cid)
    if not answer:
        raise RuntimeError(
            f"No sealed answer for {cid}. Re-run: next"
        )
    return answer


def award_flag(workspace: str | Path | None = None, *, silent: bool = False) -> str:
    """
    Call this ONLY after the student's work is verified correct.
    Writes the per-session flag into the flag file. Does not live in check source.
    """
    root = workspace_root(workspace)
    cid = current_challenge_id(root)
    flag = load_session_flag(data_dir(), cid)
    if not flag:
        raise RuntimeError(
            f"No sealed flag for {cid}. Re-run: next"
        )
    path = write_flag_file(flag)
    if not silent:
        print("Correct.")
        print(f"Flag written to: {path}")
        print("Submit the flag in the dojo UI (or: academy submit).")
    return flag


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ws = argv[0] if argv else None
    try:
        award_flag(ws)
    except Exception as exc:  # noqa: BLE001 — show to student cleanly
        print(f"award failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
