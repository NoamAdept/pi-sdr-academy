"""Flag validation helpers."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .models import Challenge, FlagSpec
from .secrets import load_session_flag


def normalize_flag(value: str) -> str:
    return value.strip()


def validate_flag(
    spec: FlagSpec,
    submitted: str,
    *,
    challenge_id: str | None = None,
    data_dir: Path | None = None,
    challenge_dir: Path | None = None,
) -> bool:
    submitted = normalize_flag(submitted)

    # Prefer sealed per-session flag whenever we have one.
    if challenge_id and data_dir is not None:
        session = load_session_flag(data_dir, challenge_id)
        if session:
            return submitted == normalize_flag(session)

    expected = normalize_flag(spec.value)
    mode = spec.validation

    if mode in ("exact", "session"):
        # session without a minted secret falls back to template (dev only)
        return submitted == expected
    if mode == "case_insensitive":
        return submitted.lower() == expected.lower()
    if mode == "regex":
        if not spec.pattern:
            return False
        return re.fullmatch(spec.pattern, submitted) is not None
    if mode == "script":
        if not spec.script or challenge_dir is None:
            return False
        script = challenge_dir / spec.script
        if not script.exists():
            return False
        result = subprocess.run(
            [str(script), submitted],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0
    return False


def validate_challenge_flag(
    challenge: Challenge,
    submitted: str,
    *,
    data_dir: Path | None = None,
) -> bool:
    challenge_dir = challenge.path.parent if challenge.path else None
    return validate_flag(
        challenge.flags,
        submitted,
        challenge_id=challenge.id,
        data_dir=data_dir,
        challenge_dir=challenge_dir,
    )
