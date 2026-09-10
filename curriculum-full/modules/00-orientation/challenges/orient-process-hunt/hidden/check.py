#!/usr/bin/env python3
"""Hidden checker — not staged into /challenge for students to read."""

from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

REQUIRED = (
    "process_number",
    "full_command",
    "folder",
    "notes_file",
    "secret_code",
)
# Accept older field names too
ALIASES = {
    "process_number": ("process_number", "pid"),
    "full_command": ("full_command", "command", "cmdline"),
    "folder": ("folder", "cwd"),
    "notes_file": ("notes_file", "brief"),
    "secret_code": ("secret_code", "token"),
}


def load_report(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    out: dict[str, str] = {}
    for canon, names in ALIASES.items():
        for name in names:
            if data.get(name):
                out[canon] = data[name]
                break
    return out


def notes_from_command(command: str) -> str:
    parts = command.split()
    for i, part in enumerate(parts):
        if part == "--notes" and i + 1 < len(parts):
            return parts[i + 1]
        # legacy name from older builds
        if part == "--brief" and i + 1 < len(parts):
            return parts[i + 1]
    return ""


def macos_folder(pid: int) -> str:
    try:
        out = subprocess.check_output(
            ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    for line in out.splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def read_live(pid: int) -> tuple[str, str, str]:
    proc = Path(f"/proc/{pid}")
    if proc.exists():
        raw = (proc / "cmdline").read_bytes()
        command = raw.replace(b"\0", b" ").decode(errors="replace").strip()
        folder = os.readlink(proc / "cwd")
        notes = ""
        parts = raw.split(b"\0")
        for i, part in enumerate(parts):
            if part in (b"--notes", b"--brief") and i + 1 < len(parts):
                notes = parts[i + 1].decode()
                break
        return command, folder, notes

    try:
        command = subprocess.check_output(
            ["ps", "-p", str(pid), "-o", "command="],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise FileNotFoundError(pid) from exc
    if not command:
        raise FileNotFoundError(pid)
    return command, macos_folder(pid), notes_from_command(command)


def norm(s: str) -> str:
    return " ".join(s.split())


def same_path(a: str, b: str) -> bool:
    try:
        return os.path.realpath(a) == os.path.realpath(b)
    except OSError:
        return os.path.normpath(a) == os.path.normpath(b)


def flag_path(challenge_dir: Path) -> Path:
    marker = challenge_dir / ".flagpath"
    if marker.is_file():
        return Path(marker.read_text(encoding="utf-8").strip())
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


def award_session_flag(challenge_dir: Path) -> None:
    """Write the sealed session flag after a correct report (no academy import needed)."""
    marker = challenge_dir / ".challenge"
    if not marker.is_file():
        return
    cid = marker.read_text(encoding="utf-8").strip()
    if not cid:
        return
    data_dir = Path(os.environ.get("ACADEMY_DATA", str(Path.home() / ".academy")))
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", cid)
    secret_path = data_dir / "secrets" / f"{safe}.json"
    if not secret_path.is_file():
        return
    try:
        payload = json.loads(secret_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    flag = payload.get("flag")
    if not isinstance(flag, str) or not flag.strip():
        return
    target = flag_path(challenge_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(flag.strip() + "\n", encoding="utf-8")
    try:
        os.chmod(target, 0o644)
    except OSError:
        pass


def main() -> int:
    challenge_dir = Path(os.environ.get("ACADEMY_WORKSPACE", ".")).resolve()
    if len(sys.argv) > 1:
        challenge_dir = Path(sys.argv[1]).resolve()

    report_path = challenge_dir / "report.txt"
    if not report_path.is_file():
        print("Missing report.txt — copy report.template to report.txt and fill it in.")
        return 1

    report = load_report(report_path)
    missing = [k for k in REQUIRED if not report.get(k)]
    if missing:
        print("Your report is incomplete. Still needed:")
        for m in missing:
            print(f"  - {m}")
        return 1

    try:
        pid = int(report["process_number"])
    except ValueError:
        print("process_number must be a whole number.")
        return 1

    try:
        command, folder, notes = read_live(pid)
    except FileNotFoundError:
        print(f"Process {pid} is not running. Did you run ./run ?")
        return 1

    errors: list[str] = []
    if "helper" not in command:
        errors.append("That process number does not look like the helper program.")
    if (
        norm(report["full_command"]) not in norm(command)
        and norm(command) not in norm(report["full_command"])
    ):
        errors.append("full_command does not match the running process.")
    if not folder or not same_path(report["folder"], folder):
        errors.append("folder does not match the running process.")
    if not notes or not same_path(report["notes_file"], notes):
        errors.append("notes_file does not match the --notes path on the command.")

    notes_file = Path(notes) if notes else Path(report["notes_file"])
    if not notes_file.is_file():
        errors.append("Could not open the notes file on disk.")
    else:
        text = notes_file.read_text(encoding="utf-8")
        code = report["secret_code"]
        if f"secret_code={code}" not in text and code not in text:
            errors.append("secret_code does not match the notes file.")

    if errors:
        print("Report not accepted yet:")
        for err in errors:
            print(f"  - {err}")
        if platform.system() == "Darwin":
            print("Mac tip: full_command → ps -p N -o command=")
            print("         folder      → lsof -a -p N -d cwd -Fn")
        else:
            print("Linux tip: full_command → /proc/N/cmdline")
            print("           folder       → readlink /proc/N/cwd")
        return 1

    print("Correct! All answers match the running process.")
    try:
        award_session_flag(challenge_dir)
    except OSError as exc:
        print(f"Note: could not write flag file ({exc}). Run Check in the dojo.", file=sys.stderr)
    print("CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
