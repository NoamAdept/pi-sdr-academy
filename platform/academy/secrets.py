"""Sealed per-session flags — never stored in the student workspace."""

from __future__ import annotations

import json
import os
import re
import secrets
from pathlib import Path
from typing import Any


def _secrets_dir(data_dir: Path) -> Path:
    path = Path(data_dir) / "secrets"
    path.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass
    return path


def prefix_from_template(flag_template: str, challenge_id: str) -> str:
    """Turn flag{foo_bar} or foo_bar into a stable prefix body."""
    text = (flag_template or "").strip()
    m = re.fullmatch(r"flag\{([^}]*)\}", text)
    body = m.group(1) if m else text
    body = re.sub(r"[^a-zA-Z0-9_]+", "_", body).strip("_")
    if not body:
        body = re.sub(r"[^a-zA-Z0-9_]+", "_", challenge_id).strip("_")
    # Drop a previous random suffix if re-minting from an old session-looking value
    body = re.sub(r"_[0-9a-f]{6}$", "", body)
    return body or "challenge"


def mint_session_flag(challenge_id: str, flag_template: str) -> str:
    prefix = prefix_from_template(flag_template, challenge_id)
    nonce = secrets.token_hex(3)  # 6 hex chars — changes every start
    return f"flag{{{prefix}_{nonce}}}"


def normalize_answer(flag_template: str) -> str:
    """Canonical recovered/puzzle answer (static template from curriculum)."""
    text = (flag_template or "").strip()
    if not text:
        return text
    if re.fullmatch(r"flag\{[^}]*\}", text):
        return text
    return f"flag{{{text}}}"


def secret_path(data_dir: Path, challenge_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", challenge_id)
    return _secrets_dir(data_dir) / f"{safe}.json"


def save_session_secret(
    data_dir: Path,
    challenge_id: str,
    *,
    flag: str,
    answer: str,
) -> Path:
    path = secret_path(data_dir, challenge_id)
    payload = {
        "challenge_id": challenge_id,
        "flag": flag,
        "answer": answer,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def save_session_flag(data_dir: Path, challenge_id: str, flag: str) -> Path:
    """Backward-compatible save (answer defaults to flag)."""
    return save_session_secret(data_dir, challenge_id, flag=flag, answer=flag)


def _load_payload(data_dir: Path, challenge_id: str) -> dict[str, Any] | None:
    path = secret_path(data_dir, challenge_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_session_flag(data_dir: Path, challenge_id: str) -> str | None:
    data = _load_payload(data_dir, challenge_id)
    if not data:
        return None
    flag = data.get("flag")
    return flag if isinstance(flag, str) and flag.strip() else None


def load_session_answer(data_dir: Path, challenge_id: str) -> str | None:
    """Puzzle answer checkers compare against (may differ from submit flag)."""
    data = _load_payload(data_dir, challenge_id)
    if not data:
        return None
    answer = data.get("answer")
    if isinstance(answer, str) and answer.strip():
        return answer.strip()
    flag = data.get("flag")
    return flag.strip() if isinstance(flag, str) and flag.strip() else None
