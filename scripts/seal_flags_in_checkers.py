#!/usr/bin/env python3
"""Strip hardcoded flags from checkers. Checkers may only exit 0/1 — academy awards flags."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "curriculum"


def strip_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    if "flag{" not in text and not re.search(r"^FLAG\s*=", text, re.M):
        return False
    orig = text

    text = re.sub(
        r'^[ \t]*FLAG\s*=\s*[ru]?[\'"]flag\{[^}]+\}[\'"].*\n',
        "",
        text,
        flags=re.MULTILINE,
    )
    # Remove string literals that are flags
    text = re.sub(r'[ru]?[\'"]flag\{[^}]+\}\\n[\'"]', "''", text)
    text = re.sub(r'[ru]?[\'"]flag\{[^}]+\}[\'"]', "''", text)

    # Neutralize writes of FLAG
    text = re.sub(
        r'[^\n]*\.write_text\(\s*FLAG\s*\+\s*[\'"]\\n[\'"][^)]*\)[^\n]*\n',
        "    print('CHECK_OK')\n",
        text,
    )
    text = re.sub(
        r'[^\n]*\.write_text\(\s*''\s*\)[^\n]*\n',
        "    print('CHECK_OK')\n",
        text,
    )
    text = re.sub(r'print\(\s*FLAG\s*\)\n', "print('CHECK_OK')\n", text)

    # award() helpers that only exist to write flags
    text = re.sub(
        r"def award\(\):\n(?:[ \t]+.+\n)+",
        "def award():\n    print('CHECK_OK')\n",
        text,
        count=1,
    )

    # Common success messages that included writing flag path content
    text = re.sub(
        r'print\([\'"]Correct! Flag written to:[\'"],\s*out\)\n',
        "print('CHECK_OK')\n",
        text,
    )
    text = re.sub(
        r'print\([\'"]Correct! Flag written to:[\'"].*\)\n',
        "print('CHECK_OK')\n",
        text,
    )
    text = re.sub(
        r'print\([\'"]Success! Flag written[^\'"]*[\'"].*\)\n',
        "print('CHECK_OK')\n",
        text,
    )
    text = re.sub(
        r'print\(f[\'"]Flag written to:.*\)\n',
        "print('CHECK_OK')\n",
        text,
    )

    if "flag{" in text:
        # last resort wipe remaining flag literals
        text = re.sub(r'flag\{[^}]+\}', 'CHECK_PLACEHOLDER', text)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "/solution/" in str(path):
            continue
        name = path.name
        if not (
            name in {"check", "check.py", "checker.py", "check_answers", "unlock"}
            or name.startswith("check")
        ):
            continue
        raw = path.read_bytes()[:4]
        if raw.startswith(b"\x7fELF") or raw.startswith(b"\xcf\xfa"):
            continue
        if strip_file(path):
            n += 1
            print("stripped", path.relative_to(ROOT.parent))
    print("stripped", n, "files")


if __name__ == "__main__":
    main()
