#!/usr/bin/env python3
"""Repair checkers after flag sealing: use expected_answer(); never write flags."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "curriculum"

HEADER = '''from pathlib import Path
import os
import sys

def _expected():
    try:
        from academy.grading import expected_answer
        return expected_answer()
    except Exception as exc:
        print("Checker cannot load sealed answer:", exc)
        print("Re-run: academy start <challenge>   then: academy verify")
        raise SystemExit(1)

'''


def repair_expected_style(text: str) -> str:
    """Checkers that used EXPECTED = 'flag{...}'."""
    if "EXPECTED" not in text:
        return text
    text = re.sub(
        r"^from pathlib import Path\nimport os\n\nEXPECTED = .*\n",
        HEADER + "EXPECTED = _expected()\n",
        text,
        count=1,
        flags=re.M,
    )
    if "EXPECTED = ''" in text or 'EXPECTED = ""' in text:
        text = text.replace("EXPECTED = ''", "EXPECTED = _expected()")
        text = text.replace('EXPECTED = ""', "EXPECTED = _expected()")
    # Drop flag-file writes; success is exit 0 for academy verify.
    text = re.sub(
        r"\nmarker = Path\(\"\.flagpath\"\).*?(?=\n(?:def |if __name__|$))",
        "\nprint('CHECK_OK')\n",
        text,
        count=1,
        flags=re.S,
    )
    # Simpler fallback: neutralize leftover out.write / flag writes
    text = re.sub(
        r"^[ \t]*out\s*=\s*Path\(.*\n(?:[ \t].*\n)*?",
        "",
        text,
        flags=re.M,
    )
    if "print('CHECK_OK')" not in text and "EXPECTED" in text:
        # ensure success path prints something
        text = re.sub(
            r"(if answer\.lower\(\) != EXPECTED\.lower\(\):.*\n.*\n)",
            r"\1print('CHECK_OK')\n",
            text,
            count=1,
        )
    return text


def repair_bpsk_style(text: str) -> str:
    """IQ checkers that compared answer to FLAG then wrote flag file."""
    if "decoded text is not the transmitted flag" not in text and "if a!=''" not in text:
        return text
    # Inject expected helper near top after imports
    if "_expected" not in text:
        text = re.sub(
            r"(from pathlib import Path\nimport os\n)",
            r"\1\n" + HEADER,
            text,
            count=1,
        )
    text = re.sub(
        r"if a\s*!=\s*''\s*:\s*fail\([\"']decoded text is not the transmitted flag[\"']\)",
        "if a != _expected(): fail('decoded text is not the transmitted flag')",
        text,
    )
    text = re.sub(
        r"if a\s*!=\s*EXPECTED",
        "if a != _expected()",
        text,
    )
    # Remove flag_path helper usage writes
    text = re.sub(
        r"\nout = flag_path\(\)\ntry:.*?except OSError:.*?\n",
        "\nprint('CHECK_OK')\n",
        text,
        count=1,
        flags=re.S,
    )
    return text


def repair_process_hunt(text: str) -> str:
    if "Report not accepted yet" not in text:
        return text
    # Replace broken award tail with clean success exit
    text = re.sub(
        r"out = flag_path\(challenge_dir\).*?return 0\n\n\nif __name__",
        "print('Correct! All answers match the running process.')\n"
        "    print('CHECK_OK')\n"
        "    print('Now run: academy verify   # unlocks the flag file')\n"
        "    print('Then:    academy submit')\n"
        "    return 0\n\n\nif __name__",
        text,
        count=1,
        flags=re.S,
    )
    # If still broken try/except from seal script
    text = re.sub(
        r"out = flag_path\(challenge_dir\)\n\s*try:\n\s*out\.parent\.mkdir.*?\n\s*print\('CHECK_OK'\)\n\s*except OSError as exc:.*?\n\s*return 0\n",
        "print('Correct! All answers match the running process.')\n"
        "    print('CHECK_OK')\n"
        "    print('Now run: academy verify')\n"
        "    print('Then:    academy submit')\n"
        "    return 0\n",
        text,
        count=1,
        flags=re.S,
    )
    return text


def clean_checker(text: str) -> str:
    text = repair_process_hunt(text)
    text = repair_expected_style(text)
    text = repair_bpsk_style(text)
    # Remove unused flag_path defs if award path gone and not referenced
    if "flag_path(" not in text.replace("def flag_path", ""):
        text = re.sub(
            r"\ndef flag_path\(\):.*?return Path\(os\.environ\.get\([^\n]+\)\n\n",
            "\n",
            text,
            count=1,
            flags=re.S,
        )
    return text


def main() -> None:
    n = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "/solution/" in str(path):
            continue
        name = path.name
        if name not in {"check", "check.py", "checker.py"} and not name.startswith("check"):
            continue
        if path.suffix in {".pyc"}:
            continue
        raw = path.read_bytes()[:4]
        if raw.startswith(b"\x7fELF") or raw.startswith(b"\xcf\xfa"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = clean_checker(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
            print("repaired", path.relative_to(ROOT.parent))
    print("repaired", n, "files")


if __name__ == "__main__":
    main()
