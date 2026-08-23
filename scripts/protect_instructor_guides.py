#!/usr/bin/env python3
"""Encrypt instructor guides behind a password (AES-256-CBC via openssl).

Public (safe to ship to student images):
  instructor/README.md
  instructor/guides.encrypted

Unlocked locally (gitignored):
  instructor/guides/
  instructor/INDEX.md

Usage:
  export INSTRUCTOR_PASSWORD='your-secret'   # optional; else prompted / generated
  python3 scripts/lock_instructor_guides.py
  python3 scripts/unlock_instructor_guides.py
"""

from __future__ import annotations

import getpass
import os
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUCTOR = ROOT / "instructor"
ENC_PATH = INSTRUCTOR / "guides.encrypted"
PASSWORD_FILE = INSTRUCTOR / ".instructor_password"
PLAIN_GUIDES = INSTRUCTOR / "guides"
PLAIN_INDEX = INSTRUCTOR / "INDEX.md"


def _openssl() -> str:
    for candidate in ("openssl", "/usr/bin/openssl", "/usr/local/bin/openssl"):
        if shutil.which(candidate) or Path(candidate).is_file():
            return candidate if "/" in candidate or candidate == "openssl" else candidate
    # resolve which
    path = shutil.which("openssl")
    if not path:
        raise SystemExit("openssl not found — required to encrypt instructor guides")
    return path


def resolve_password(*, generate_if_missing: bool) -> str:
    env = os.environ.get("INSTRUCTOR_PASSWORD", "").strip()
    if env:
        return env
    if PASSWORD_FILE.is_file():
        pw = PASSWORD_FILE.read_text(encoding="utf-8").strip()
        if pw:
            return pw
    if generate_if_missing:
        pw = secrets.token_urlsafe(18)
        PASSWORD_FILE.write_text(pw + "\n", encoding="utf-8")
        try:
            PASSWORD_FILE.chmod(0o600)
        except OSError:
            pass
        print(f"[+] generated password → {PASSWORD_FILE}  (gitignored; save this!)")
        print(f"    password: {pw}")
        return pw
    try:
        pw = getpass.getpass("Instructor password: ")
    except (EOFError, KeyboardInterrupt) as exc:
        raise SystemExit("password required") from exc
    if not pw:
        raise SystemExit("empty password")
    return pw


def pack_plaintext(tar_path: Path) -> None:
    if not PLAIN_GUIDES.is_dir():
        raise SystemExit(f"missing {PLAIN_GUIDES} — run: python3 scripts/generate_instructor_guides.py")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(PLAIN_GUIDES, arcname="guides")
        if PLAIN_INDEX.is_file():
            tar.add(PLAIN_INDEX, arcname="INDEX.md")


def encrypt_file(src: Path, dest: Path, password: str) -> None:
    openssl = _openssl()
    # AES-256-CBC + PBKDF2; password via env to avoid argv exposure in ps
    env = os.environ.copy()
    env["INSTRUCTOR_PASSWORD"] = password
    cmd = [
        openssl,
        "enc",
        "-aes-256-cbc",
        "-pbkdf2",
        "-iter",
        "600000",
        "-salt",
        "-in",
        str(src),
        "-out",
        str(dest),
        "-pass",
        "env:INSTRUCTOR_PASSWORD",
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"openssl encrypt failed:\n{result.stderr}")


def decrypt_file(src: Path, dest: Path, password: str) -> None:
    openssl = _openssl()
    env = os.environ.copy()
    env["INSTRUCTOR_PASSWORD"] = password
    cmd = [
        openssl,
        "enc",
        "-d",
        "-aes-256-cbc",
        "-pbkdf2",
        "-iter",
        "600000",
        "-in",
        str(src),
        "-out",
        str(dest),
        "-pass",
        "env:INSTRUCTOR_PASSWORD",
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(
            "decrypt failed (wrong password or corrupt archive)\n" + (result.stderr or "")
        )


def remove_plaintext() -> None:
    if PLAIN_GUIDES.exists():
        shutil.rmtree(PLAIN_GUIDES)
    if PLAIN_INDEX.exists():
        PLAIN_INDEX.unlink()


def lock() -> None:
    # Ensure guides exist
    if not PLAIN_GUIDES.is_dir():
        print("[*] generating guides first…")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_instructor_guides.py")],
            check=True,
        )
    password = resolve_password(generate_if_missing=True)
    INSTRUCTOR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "instructor-guides.tar.gz"
        pack_plaintext(tar_path)
        encrypt_file(tar_path, ENC_PATH, password)
    remove_plaintext()
    write_public_readme()
    print(f"[+] locked → {ENC_PATH}")
    print("[+] plaintext guides removed from disk")
    print("[*] unlock with: python3 scripts/unlock_instructor_guides.py")


def unlock() -> None:
    if not ENC_PATH.is_file():
        raise SystemExit(f"missing encrypted archive: {ENC_PATH}")
    password = resolve_password(generate_if_missing=False)
    with tempfile.TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "instructor-guides.tar.gz"
        decrypt_file(ENC_PATH, tar_path, password)
        # Clear old plaintext first
        remove_plaintext()
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(INSTRUCTOR)
    print(f"[+] unlocked guides → {PLAIN_GUIDES}")
    if PLAIN_INDEX.is_file():
        print(f"[+] index → {PLAIN_INDEX}")


def write_public_readme() -> None:
    text = """# Instructor materials (password protected)

**Students must not receive the unlocked guides.**

The detailed solution walkthroughs are stored as an **AES-256 encrypted** archive:

- `guides.encrypted` — locked instructor pack (safe to keep on an instructor USB / private mirror)
- `guides/` + `INDEX.md` — appear only after unlock (gitignored)

## Unlock (instructors / TAs)

```bash
cd /path/to/pi-sdr-academy
export INSTRUCTOR_PASSWORD='…'          # or you will be prompted
python3 scripts/unlock_instructor_guides.py
```

Then open:

- `instructor/INDEX.md`
- `instructor/guides/<module>/<challenge-id>.md`

## Lock again (after regenerating)

```bash
python3 scripts/generate_instructor_guides.py
export INSTRUCTOR_PASSWORD='…'          # same password, or omit to reuse/generate
python3 scripts/lock_instructor_guides.py
```

## Password storage

- Prefer `INSTRUCTOR_PASSWORD` in your shell / password manager.
- A local file `instructor/.instructor_password` may be created on first lock — **gitignored**, never ship to student Pis.

## Crypto

`openssl enc -aes-256-cbc -pbkdf2 -iter 600000` over a gzip tar of `guides/` + `INDEX.md`.
"""
    (INSTRUCTOR / "README.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    name = Path(sys.argv[0]).name
    if "unlock" in name or (argv and argv[0] == "unlock"):
        unlock()
    elif "lock" in name or (argv and argv[0] == "lock"):
        lock()
    else:
        # default by script name association
        if "unlock" in name:
            unlock()
        else:
            lock()
    return 0


if __name__ == "__main__":
    # Separate entry files call lock()/unlock(); this file supports both.
    raise SystemExit(main())
