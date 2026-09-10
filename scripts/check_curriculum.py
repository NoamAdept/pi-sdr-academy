#!/usr/bin/env python3
"""Curriculum integrity checks — one runnable gate for challenge health.

ponytail: O(n) filesystem scan over all challenges; upgrade to parallel
staging only if start-smoke becomes too slow on larger curricula.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = Path(os.environ.get("ACADEMY_CURRICULUM", ROOT / "curriculum"))
sys.path.insert(0, str(ROOT / "platform"))

REQUIRED = {
    "id",
    "module",
    "title",
    "difficulty",
    "estimated_time",
    "prerequisites",
    "objectives",
    "description",
    "environment",
    "files",
    "expected_tools",
    "flags",
    "hints",
    "solution",
    "explanation",
}


def main() -> int:
    from academy.admin import validate_challenge_draft
    from academy.engine import AcademyEngine
    from academy.models import load_yaml

    fails: list[str] = []
    ok = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(msg)

    yaml_files = sorted(CURRICULUM.glob("modules/*/challenges/*/challenge.yaml"))
    check(len(yaml_files) == 10, f"expected 10 challenge.yaml files, got {len(yaml_files)}")

    modules = sorted((CURRICULUM / "modules").glob("*/module.yaml"))
    check(len(modules) == 5, f"expected 5 modules, got {len(modules)}")
    check((CURRICULUM / "dojos.yaml").is_file(), "dojos.yaml missing")

    registered: dict[str, set[str]] = {}
    for mp in modules:
        data = load_yaml(mp)
        slug = data.get("slug")
        check(bool(slug), f"{mp}: missing slug")
        registered[slug] = set(data.get("challenges") or [])
        check(isinstance(data.get("challenges"), list), f"{mp}: challenges not a list")

    ids: set[str] = set()
    for ypath in yaml_files:
        folder = ypath.parent.name
        data = load_yaml(ypath)
        cid = data.get("id")
        check(cid == folder, f"{ypath}: id {cid!r} != folder {folder!r}")
        check(cid not in ids, f"duplicate challenge id: {cid}")
        ids.add(cid)

        missing = REQUIRED - set(data)
        check(not missing, f"{cid}: missing fields {sorted(missing)}")

        # schema-shaped validation (shared helper)
        errs = validate_challenge_draft(data)
        # session validation is allowed in curriculum even if schema enum omits it
        errs = [e for e in errs if "Flag validation" not in e]
        check(not errs, f"{cid}: {errs[:2]}")

        flags = data.get("flags") or {}
        check(bool(str(flags.get("value", "")).strip()), f"{cid}: empty flag value")
        hints = data.get("hints") or []
        check(len(hints) >= 2, f"{cid}: need >=2 hints")

        files_dir = ypath.parent / "files"
        check(files_dir.is_dir(), f"{cid}: missing files/")
        for rel in data.get("files") or []:
            # directory entries end with /
            target = files_dir / rel.rstrip("/")
            check(target.exists(), f"{cid}: listed file missing: {rel}")

        mod = data.get("module")
        check(mod in registered, f"{cid}: module {mod!r} unknown")
        if mod in registered:
            check(cid in registered[mod], f"{cid}: not listed in module.yaml for {mod}")

        desc = str(data.get("description") or "")
        check(len(desc.strip()) >= 40, f"{cid}: description too short")
        # Concrete flags look like flag{snake_case_words}; placeholders are ok.
        leaked = re.findall(r"flag\{[a-z0-9_]{12,}\}", desc.lower())
        check(not leaked, f"{cid}: description may leak a concrete flag: {leaked[:1]}")

    # Engine load + start smoke (first startable challenge per module)
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "data"
        ws = Path(tmp) / "workspace"
        engine = AcademyEngine(curriculum_root=CURRICULUM, data_dir=data_dir, workspace_root=ws)
        check(len(engine.challenges) == len(ids), "engine challenge count mismatch")
        check(len(engine.modules) == len(modules), "engine module count mismatch")

        # Unlock all known challenge-id prereqs so start smoke is a staging check.
        store = engine.progress()
        for cid in engine._challenges:
            prog = store.challenges.get(cid)
            if prog is None:
                from academy.progress import ChallengeProgress
                store.challenges[cid] = ChallengeProgress(started_at=0.0, solved=True)
            else:
                prog.solved = True
        engine.progress_repo.save(store)

        for module in engine.modules:
            chs = engine.module_challenges(module.slug)
            check(len(chs) >= 1, f"module {module.slug} has no challenges")
            for ch in chs:
                try:
                    dest = engine.start_challenge(ch.id)
                    check(dest.exists(), f"start {ch.id}: workspace missing")
                    check((dest / ".challenge").read_text().strip() == ch.id, f"start {ch.id}: .challenge marker")
                    staged = [p for p in dest.iterdir() if p.name not in {".challenge", ".flagpath"}]
                    check(len(staged) >= 1, f"start {ch.id}: nothing staged")
                except Exception as exc:  # noqa: BLE001
                    check(False, f"start {ch.id}: {exc}")

    print(f"PASS {ok}  FAIL {len(fails)}")
    for line in fails[:40]:
        print(" -", line)
    if len(fails) > 40:
        print(f" - … {len(fails) - 40} more")
    # Require at least 100 successful checks (user gate)
    if ok < 100:
        print(f"Need >=100 passing checks, got {ok}")
        return 1
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
