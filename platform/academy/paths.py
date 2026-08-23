"""Shared paths for challenge workspace and flag file."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def _can_use_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".academy_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def resolve_workspace() -> Path:
    """Prefer /challenge; fall back to ~/challenge when not writable."""
    env = os.environ.get("ACADEMY_WORKSPACE")
    if env:
        p = Path(env)
        p.mkdir(parents=True, exist_ok=True)
        return p
    for candidate in (Path("/challenge"), Path.home() / "challenge"):
        if _can_use_dir(candidate):
            return candidate
    # Last resort
    p = Path(tempfile.gettempdir()) / "academy-challenge"
    p.mkdir(parents=True, exist_ok=True)
    return p


def resolve_flag_path() -> Path:
    """Prefer /home/flag.txt; fall back to ~/flag.txt when not writable."""
    env = os.environ.get("ACADEMY_FLAG_PATH")
    if env:
        return Path(env)
    preferred = Path("/home/flag.txt")
    try:
        preferred.parent.mkdir(parents=True, exist_ok=True)
        if os.access(preferred.parent, os.W_OK):
            return preferred
    except OSError:
        pass
    return Path.home() / "flag.txt"


def read_flag_file(path: Path | None = None) -> str | None:
    path = path or resolve_flag_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def write_flag_file(flag: str, path: Path | None = None) -> Path:
    path = path or resolve_flag_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(flag.strip() + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass
    return path
