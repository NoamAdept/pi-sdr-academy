#!/usr/bin/env python3
"""Generate instructor solution guides for every challenge.

Output: instructor/guides/<module-dir>/<challenge-id>.md
Also writes instructor/INDEX.md and refreshes instructor/README.md sections.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum" / "modules"
DOJOS = ROOT / "curriculum" / "dojos.yaml"
OUT = ROOT / "instructor"
GUIDES = OUT / "guides"


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def module_dirs() -> list[Path]:
    return sorted(
        p for p in CURRICULUM.iterdir() if p.is_dir() and (p / "module.yaml").exists()
    )


def challenge_dirs(module_path: Path) -> list[Path]:
    root = module_path / "challenges"
    if not root.is_dir():
        return []
    return sorted(
        p for p in root.iterdir() if p.is_dir() and (p / "challenge.yaml").exists()
    )


def first_paragraph(text: str, limit: int = 600) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    # skip leading pure headings if possible
    for p in parts:
        if p.startswith("#"):
            continue
        body = " ".join(p.split())
        if len(body) > limit:
            return body[: limit - 1].rstrip() + "…"
        return body
    body = " ".join(parts[0].split()) if parts else ""
    return body[:limit]


def read_solution_artifacts(chal_dir: Path) -> list[tuple[str, str]]:
    """Return (relative_name, fenced_content) for solution/ files."""
    sdir = chal_dir / "solution"
    if not sdir.is_dir():
        return []
    out: list[tuple[str, str]] = []
    for path in sorted(sdir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".pyc", ".o", ".so", ".iq", ".npy", ".npz"}:
            continue
        if path.stat().st_size > 80_000:
            out.append((str(path.relative_to(chal_dir)), "_File too large to inline; open in curriculum._"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            out.append((str(path.relative_to(chal_dir)), "_Binary / non-text artifact._"))
            continue
        lang = {
            ".py": "python",
            ".sh": "bash",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".md": "markdown",
            ".txt": "text",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
        }.get(path.suffix.lower(), "")
        fence = f"```{lang}\n{text.rstrip()}\n```" if lang or text else f"```\n{text.rstrip()}\n```"
        out.append((str(path.relative_to(chal_dir)), fence))
    return out


def dojo_for_module(slug: str) -> str | None:
    if not DOJOS.is_file():
        return None
    data = load_yaml(DOJOS)
    for section in ("core", "side_quests"):
        for d in data.get(section) or []:
            if slug in (d.get("modules") or []):
                return f"{d.get('belt_label', '')} — {d.get('title', d.get('id'))}".strip(" —")
    return None


def render_guide(
    *,
    module: dict,
    module_dir_name: str,
    chal: dict,
    chal_dir: Path,
) -> str:
    cid = chal["id"]
    title = chal.get("title", cid)
    difficulty = chal.get("difficulty", "")
    eta = chal.get("estimated_time", "")
    objectives = chal.get("objectives") or []
    mastery = chal.get("mastery_evidence") or []
    prereqs = chal.get("prerequisites") or []
    tools = chal.get("expected_tools") or []
    hints = chal.get("hints") or []
    solution = (chal.get("solution") or "").strip()
    explanation = (chal.get("explanation") or "").strip()
    extension = chal.get("extension") or {}
    flags = chal.get("flags") or {}
    env = chal.get("environment") or {}
    files = chal.get("files") or []
    perf = (chal.get("performance_notes") or "").strip()
    hardware = chal.get("optional_hardware") or []

    flag_value = flags.get("value", "")
    flag_mode = flags.get("validation", "session")
    plant = flags.get("plant_files") or []

    dojo = dojo_for_module(module.get("slug", ""))
    artifacts = read_solution_artifacts(chal_dir)

    lines: list[str] = []
    lines.append(f"# Instructor Guide — {title}")
    lines.append("")
    lines.append(f"**Challenge ID:** `{cid}`  ")
    lines.append(f"**Module:** {module.get('title', '')} (`{module.get('slug', '')}`)  ")
    if dojo:
        lines.append(f"**Dojo / belt:** {dojo}  ")
    lines.append(f"**Difficulty:** {difficulty} · **Est. time:** {eta}  ")
    lines.append(f"**Curriculum path:** `curriculum/modules/{module_dir_name}/challenges/{cid}/`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Purpose (what students should learn)")
    lines.append("")
    if objectives:
        for o in objectives:
            lines.append(f"- `{o}`")
    else:
        lines.append("_No formal objectives listed — use the mission text below._")
    lines.append("")
    if mastery:
        lines.append("**Mastery evidence tags:** " + ", ".join(f"`{m}`" for m in mastery))
        lines.append("")
    lines.append("## Mission (student-facing)")
    lines.append("")
    lines.append((chal.get("description") or "").strip() or "_No description._")
    lines.append("")
    lines.append("## Teaching notes before they start")
    lines.append("")
    lines.append("- Workspace is always the shared challenge folder (`/challenge` or `~/challenge`).")
    lines.append("- Session flags are randomized on `next` / `start`. The curriculum template below is the **answer shape**, not necessarily the submit string.")
    lines.append("- Preferred student scoring path: solve → `./check` (auto-submits) or `./submit 'flag{...}'` for find-style puzzles.")
    if prereqs:
        lines.append("- **Declared prerequisites:** " + ", ".join(f"`{p}`" for p in prereqs))
    if tools:
        lines.append("- **Expected tools:** " + ", ".join(f"`{t}`" for t in tools))
    if env:
        lines.append(f"- **Environment type:** `{env.get('type', 'workspace')}`")
        if env.get("notes"):
            lines.append(f"- **Env notes:** {env['notes'].strip()}")
    if files:
        lines.append("- **Starter files (from `files/`):** " + ", ".join(f"`{f}`" for f in files[:20]))
        if len(files) > 20:
            lines.append(f"  - …and {len(files) - 20} more")
    lines.append("")
    lines.append("## Progressive hints (reveal only if stuck)")
    lines.append("")
    if hints:
        for h in sorted(hints, key=lambda x: x.get("level", 0)):
            lvl = h.get("level", "?")
            text = (h.get("text") or "").strip()
            lines.append(f"### Hint {lvl}")
            lines.append("")
            lines.append(text)
            lines.append("")
    else:
        lines.append("_No authored hints._")
        lines.append("")

    lines.append("## Solution walkthrough (instructor)")
    lines.append("")
    lines.append(
        "Walk the student through this path, or demonstrate after they finish. "
        "Prefer asking *why* each step works before pasting commands."
    )
    lines.append("")
    if solution:
        lines.append(solution)
        lines.append("")
    else:
        lines.append("_No solution field in YAML — use reference artifacts below._")
        lines.append("")

    lines.append("## Conceptual explanation")
    lines.append("")
    if explanation:
        lines.append(explanation)
        lines.append("")
    else:
        lines.append("_No explanation field authored._")
        lines.append("")

    lines.append("## Flag & grading")
    lines.append("")
    lines.append(f"- **Template / educational flag:** `{flag_value}`")
    lines.append(f"- **Validation mode:** `{flag_mode}` (session flags append a random `_xxxxxx` nonce at start time)")
    if plant:
        lines.append("- **Planted into puzzle files at start:**")
        for p in plant:
            lines.append(f"  - `{p}`")
    lines.append(
        "- Checkers must **not** hardcode the session flag. Decode-style challenges "
        "compare recovered text to the sealed **answer** (template); `./check` then awards the session flag."
    )
    lines.append("")

    if artifacts:
        lines.append("## Reference solution artifacts")
        lines.append("")
        lines.append("Copied from the challenge `solution/` directory for grading / demos.")
        lines.append("")
        for name, body in artifacts:
            lines.append(f"### `{name}`")
            lines.append("")
            lines.append(body)
            lines.append("")

    if extension:
        lines.append("## Extension (optional stretch)")
        lines.append("")
        if extension.get("title"):
            lines.append(f"**{extension['title']}**")
            lines.append("")
        if extension.get("description"):
            lines.append(extension["description"].strip())
            lines.append("")

    lines.append("## Common failure modes")
    lines.append("")
    lines.append("- Student runs commands outside the challenge workspace — remind them `cd` into the folder from `next`.")
    lines.append("- Submitting the curriculum template flag after a fresh `next` (nonce changed) — they must use the planted/session flag or re-run `./check`.")
    lines.append("- zsh brace expansion: `./submit 'flag{...}'` needs quotes.")
    if "chmod" in " ".join(tools).lower() or "permission" in title.lower():
        lines.append("- Permission puzzles: they own the file; `sudo` is not required and should be discouraged.")
    if any(x in cid for x in ("bpsk", "qpsk", "sync", "rx-", "iq-", "filt-", "fft-", "pulse-", "proto-", "ctf-")):
        lines.append("- DSP/IQ: confirm `answer.txt` format (exact string / numeric) matches the checker before debugging the signal chain.")
        lines.append("- Sample rate / samples-per-symbol mismatches — have them print array lengths and `fs` from the briefing.")
    if any(x in cid for x in ("cmake-", "c-", "cpp-", "gdb-")):
        lines.append("- Build failures: missing packages offline — use the academy offline bundle; do not send them to the Internet.")
    lines.append("")

    if perf or hardware:
        lines.append("## Lab constraints")
        lines.append("")
        if perf:
            lines.append(perf)
            lines.append("")
        if hardware:
            lines.append("**Optional hardware:** " + ", ".join(str(h) for h in hardware))
            lines.append("")

    lines.append("## Demo checklist")
    lines.append("")
    lines.append("1. `next` (or `academy start " + cid + "`) on a clean workspace.")
    lines.append("2. Show the briefing / README without revealing the flag.")
    lines.append("3. Solve live (or from this guide), narrating *why*.")
    lines.append("4. Run `./check` and confirm celebration / progress.")
    lines.append("5. Ask one transfer question from **Conceptual explanation** or **Extension**.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("_Generated for instructors. Do not distribute this directory to students._")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    GUIDES.mkdir(parents=True, exist_ok=True)
    index_rows: list[tuple[int, str, str, str, str, str]] = []
    # order, module_slug, module_title, cid, title, rel_path

    count = 0
    for mdir in module_dirs():
        meta = load_yaml(mdir / "module.yaml")
        out_mod = GUIDES / mdir.name
        out_mod.mkdir(parents=True, exist_ok=True)
        # module index
        mod_lines = [
            f"# {meta.get('title', mdir.name)} — Instructor Guides",
            "",
            f"Module slug: `{meta.get('slug', '')}` · order `{meta.get('order', '')}`",
            "",
            (meta.get("description") or "").strip(),
            "",
            "| Challenge | Difficulty | Guide |",
            "|-----------|------------|-------|",
        ]
        for cdir in challenge_dirs(mdir):
            chal = load_yaml(cdir / "challenge.yaml")
            cid = chal["id"]
            guide = render_guide(
                module=meta,
                module_dir_name=mdir.name,
                chal=chal,
                chal_dir=cdir,
            )
            path = out_mod / f"{cid}.md"
            path.write_text(guide, encoding="utf-8")
            rel = path.relative_to(OUT).as_posix()
            count += 1
            index_rows.append(
                (
                    int(meta.get("order", 999)),
                    str(meta.get("slug", "")),
                    str(meta.get("title", "")),
                    cid,
                    str(chal.get("title", cid)),
                    rel,
                )
            )
            mod_lines.append(
                f"| `{cid}` | {chal.get('difficulty', '')} | [{chal.get('title', cid)}]({cid}.md) |"
            )
        mod_lines.append("")
        (out_mod / "README.md").write_text("\n".join(mod_lines) + "\n", encoding="utf-8")

    index_rows.sort(key=lambda r: (r[0], r[3]))
    idx = [
        "# Instructor Guide Index",
        "",
        f"**{count} challenges** — complete solution walkthroughs for educators.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        "python3 scripts/generate_instructor_guides.py",
        "```",
        "",
        "| # | Module | Challenge | Guide |",
        "|---|--------|-----------|-------|",
    ]
    for order, slug, mtitle, cid, title, rel in index_rows:
        idx.append(f"| {order:02d} | {mtitle} | `{cid}` — {title} | [{cid}.md]({rel}) |")
    idx.append("")
    (OUT / "INDEX.md").write_text("\n".join(idx) + "\n", encoding="utf-8")

    # Avoid clobbering the short public README used when guides are encrypted.
    if not (OUT / "guides.encrypted").is_file():
        readme = f"""# Instructor materials

**Students must not receive unlocked guides.**

```bash
python3 scripts/generate_instructor_guides.py
python3 scripts/lock_instructor_guides.py
python3 scripts/unlock_instructor_guides.py   # when teaching
```

Generated (plaintext, lock before shipping): **{count}**.
"""
        (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Wrote {count} instructor guides → {OUT}")
    if (OUT / "guides.encrypted").is_file():
        print("Note: run python3 scripts/lock_instructor_guides.py to re-encrypt")


if __name__ == "__main__":
    main()
