"""Dojos + belt progression (pwn.college-inspired curriculum map)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .engine import AcademyEngine
from .progress import ProgressStore
from .ui_flavor import display_title


BELT_COLORS = {
    "white": "#f2f2f2",
    "yellow": "#e6c84a",
    "orange": "#e08a3c",
    "green": "#2f6b3a",
    "blue": "#3b7dd8",
    "purple": "#8b5cf6",
    "brown": "#8b5a2b",
    "black": "#222222",
}


@dataclass
class DojoSpec:
    id: str
    title: str
    belt: str
    belt_label: str
    tagline: str
    modules: list[str]
    kind: str = "core"  # core | side


@dataclass
class DojoCatalog:
    intro: str
    rules: str
    core: list[DojoSpec]
    side_quests: list[DojoSpec]

    @property
    def all(self) -> list[DojoSpec]:
        return [*self.core, *self.side_quests]


def load_dojos(curriculum_root: Path) -> DojoCatalog:
    path = Path(curriculum_root) / "dojos.yaml"
    if not path.is_file():
        return DojoCatalog(intro="", rules="", core=[], side_quests=[])
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def parse(items: list[dict[str, Any]] | None, kind: str) -> list[DojoSpec]:
        out: list[DojoSpec] = []
        for item in items or []:
            out.append(
                DojoSpec(
                    id=str(item["id"]),
                    title=str(item["title"]),
                    belt=str(item.get("belt", "white")),
                    belt_label=str(item.get("belt_label", item.get("belt", "belt")).title()),
                    tagline=str(item.get("tagline", "")).strip(),
                    modules=[str(m) for m in item.get("modules", [])],
                    kind=kind,
                )
            )
        return out

    return DojoCatalog(
        intro=str(raw.get("intro", "")).strip(),
        rules=str(raw.get("rules", "")).strip(),
        core=parse(raw.get("core"), "core"),
        side_quests=parse(raw.get("side_quests"), "side"),
    )


@dataclass
class DojoStats:
    id: str
    title: str
    belt: str
    belt_label: str
    belt_color: str
    tagline: str
    kind: str
    modules: int
    challenges: int
    solved: int
    locked: bool
    next_challenge_id: str | None = None
    module_slugs: list[str] = field(default_factory=list)


def _module_challenge_ids(engine: AcademyEngine, slug: str) -> list[str]:
    return [c.id for c in engine.module_challenges(slug)]


def dojo_stats(engine: AcademyEngine, store: ProgressStore | None = None) -> list[DojoStats]:
    store = store or engine.progress()
    catalog = load_dojos(engine.curriculum_root)
    result: list[DojoStats] = []

    for spec in catalog.all:
        ch_ids: list[str] = []
        for slug in spec.modules:
            try:
                ch_ids.extend(_module_challenge_ids(engine, slug))
            except KeyError:
                continue
        solved = sum(
            1
            for cid in ch_ids
            if (p := store.challenges.get(cid)) and p.solved
        )
        next_id = None
        for cid in ch_ids:
            prog = store.challenges.get(cid)
            if not prog or not prog.solved:
                next_id = cid
                break
        result.append(
            DojoStats(
                id=spec.id,
                title=spec.title,
                belt=spec.belt,
                belt_label=spec.belt_label,
                belt_color=BELT_COLORS.get(spec.belt, "#888"),
                tagline=spec.tagline,
                kind=spec.kind,
                modules=len(spec.modules),
                challenges=len(ch_ids),
                solved=solved,
                locked=False,
                next_challenge_id=next_id,
                module_slugs=list(spec.modules),
            )
        )

    # Core dojos unlock sequentially; side quests stay open.
    prior_complete = True
    for stats in result:
        if stats.kind != "core":
            stats.locked = False
            continue
        stats.locked = not prior_complete
        complete = stats.challenges > 0 and stats.solved >= stats.challenges
        if not complete:
            prior_complete = False

    return result


def _read_challenge_readme(challenge) -> str:
    if not challenge.path:
        return ""
    files_dir = challenge.path.parent / "files"
    for name in ("README.txt", "README.md"):
        path = files_dir / name
        if path.is_file():
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                return ""
    return ""


def _clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            if lines and lines[-1] != "":
                lines.append("")
            continue
        stripped = line.strip()
        if set(stripped) <= {"=", "-", "*"}:
            continue
        if stripped.startswith("```"):
            continue
        lines.append(stripped)
    # trim leading/trailing blanks
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def challenge_ui_copy(challenge) -> dict[str, Any]:
    """Short mission + steps for the dojo UI (student-facing, brief)."""
    readme = _read_challenge_readme(challenge)
    desc = (challenge.description or "").strip()
    source = readme.strip() or desc

    lines = _clean_lines(source)
    # Drop a lone title line that matches the challenge title
    if lines and lines[0].lower().strip("# ") in {
        (challenge.title or "").lower(),
        display_title(challenge.id, challenge.title or "").lower(),
    }:
        lines = lines[1:]
        while lines and lines[0] == "":
            lines.pop(0)

    steps: list[str] = []
    mission_parts: list[str] = []
    in_workflow = False
    skip_cmd_block = False
    for line in lines:
        low = line.lower().rstrip(":")
        if low in {"workflow", "steps", "what to do"} or low.startswith("workflow"):
            in_workflow = True
            skip_cmd_block = False
            continue
        if in_workflow:
            step = line.lstrip("0123456789.-) ").strip()
            if step:
                steps.append(step)
            continue

        # Skip fenced-looking command-only blocks from READMEs (indented tool lists)
        if line.startswith("  ") or (
            len(line.split()) <= 4
            and all(tok.startswith((".", "/", "`")) or tok in {"pwd", "ls", "cd", "find", "cat", "FILE", "-la", "-type", "f"} for tok in line.replace("`", "").split())
        ):
            # bare command lines — fold into tools/steps later, not mission prose
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            if heading in {"mission", "task", "goal"}:
                continue
            continue

        # Cut submit / academy boilerplate
        if any(
            k in line.lower()
            for k in (
                "academy submit",
                "flagpath",
                "printf ",
                "or submit it directly",
                "copy it to the academy flag",
                "when you find a value shaped like",
                "when you find it, either",
            )
        ):
            skip_cmd_block = True
            continue
        if skip_cmd_block:
            continue
        if line.startswith("**Useful") or line.startswith("**Challenge"):
            continue
        mission_parts.append(line)

    mission = " ".join(mission_parts)
    mission = " ".join(mission.split())
    # Drop dangling lead-ins left after stripping command lists
    mission = mission.rstrip(":").rstrip()
    for tail in ("Explore with", "Use", "Tools", "Try"):
        if mission.lower().endswith(tail.lower()):
            mission = mission[: -len(tail)].rstrip(" :")
            break

    # Keep ~3 sentences max — enough detail, still brief
    sentences = [
        s.strip()
        for s in mission.replace("?", "?|").replace("!", "!|").replace(". ", ".|").split("|")
        if s.strip()
    ]
    mission = " ".join(sentences[:3]).strip()
    if len(mission) > 380:
        mission = mission[:377].rstrip() + "…"

    blurb = " ".join(sentences[:2]).strip() if sentences else (challenge.title or challenge.id or "Challenge")
    if blurb and not blurb.endswith((".", "!", "?")):
        blurb += "."
    if len(blurb) > 220:
        blurb = blurb[:217].rstrip() + "…"

    clean_steps: list[str] = []
    for step in steps[:5]:
        s = " ".join(step.replace("`", "").split())
        if len(s) > 110:
            s = s[:107].rstrip() + "…"
        clean_steps.append(s)

    if not clean_steps:
        clean_steps = [
            "Press Start — files land in the challenge folder",
            "Open that folder, read README.txt, solve it",
            "Press Done",
        ]

    return {
        "blurb": blurb or (challenge.title or ""),
        "mission": mission or blurb,
        "steps": clean_steps,
    }


def dojo_detail(engine: AcademyEngine, dojo_id: str) -> dict[str, Any] | None:
    """Full dojo payload with modules + challenge blurbs for the web UI."""
    store = engine.progress()
    stats_list = dojo_stats(engine, store)
    stats = next((d for d in stats_list if d.id == dojo_id), None)
    if stats is None:
        return None

    modules_out: list[dict[str, Any]] = []
    for slug in stats.module_slugs:
        try:
            module = engine.get_module(slug)
        except KeyError:
            continue
        chs = []
        for c in engine.module_challenges(slug):
            prog = store.challenges.get(c.id)
            copy = challenge_ui_copy(c)
            chs.append(
                {
                    "id": c.id,
                    "title": display_title(c.id, c.title),
                    "difficulty": c.difficulty,
                    "estimated_time": c.estimated_time,
                    "description": copy["blurb"],
                    "mission": copy["mission"],
                    "steps": copy["steps"],
                    "expected_tools": list(c.expected_tools or [])[:8],
                    "prerequisites": list(c.prerequisites or []),
                    "hints_total": len(c.hints or []),
                    "hints_revealed": int(prog.hints_revealed) if prog else 0,
                    "solved": bool(prog and prog.solved),
                    "thumb": f"/api/thumbs/{c.id}.svg",
                }
            )
        modules_out.append(
            {
                "slug": module.slug,
                "title": module.title,
                "description": (module.description or "").strip(),
                "order": module.order,
                "challenges": chs,
            }
        )

    return {
        "id": stats.id,
        "title": stats.title,
        "belt": stats.belt,
        "belt_label": stats.belt_label,
        "belt_color": stats.belt_color,
        "tagline": stats.tagline,
        "kind": stats.kind,
        "modules": stats.modules,
        "challenges": stats.challenges,
        "solved": stats.solved,
        "locked": stats.locked,
        "next_challenge_id": stats.next_challenge_id,
        "module_slugs": stats.module_slugs,
        "modules_detail": modules_out,
    }


def next_dojo(engine: AcademyEngine) -> DojoStats | None:
    for d in dojo_stats(engine):
        if d.kind != "core":
            continue
        if d.locked:
            continue
        if d.solved < d.challenges:
            return d
    return None


def next_challenge_payload(engine: AcademyEngine) -> dict[str, Any] | None:
    """Single 'do this next' card for the minimal dojo UI."""
    dojo = next_dojo(engine)
    if dojo is None or not dojo.next_challenge_id:
        return None
    try:
        ch = engine.get_challenge(dojo.next_challenge_id)
    except KeyError:
        return None
    copy = challenge_ui_copy(ch)
    store = engine.progress()
    return {
        "dojo_id": dojo.id,
        "dojo_title": dojo.title,
        "belt": dojo.belt,
        "belt_label": dojo.belt_label,
        "belt_color": dojo.belt_color,
        "id": ch.id,
        "title": display_title(ch.id, ch.title),
        "mission": copy["mission"],
        "steps": copy["steps"],
        "hints_total": len(ch.hints or []),
        "workspace": store.current_workspace if store.current_challenge_id == ch.id else None,
        "started": store.current_challenge_id == ch.id,
    }


def catalog_payload(engine: AcademyEngine) -> dict[str, Any]:
    catalog = load_dojos(engine.curriculum_root)
    stats = dojo_stats(engine)
    nxt = next_dojo(engine)
    return {
        "intro": catalog.intro,
        "rules": catalog.rules,
        "dojos": [
            {
                "id": d.id,
                "title": d.title,
                "belt": d.belt,
                "belt_label": d.belt_label,
                "belt_color": d.belt_color,
                "tagline": d.tagline,
                "kind": d.kind,
                "modules": d.modules,
                "challenges": d.challenges,
                "solved": d.solved,
                "locked": d.locked,
                "next_challenge_id": d.next_challenge_id,
                "module_slugs": d.module_slugs,
            }
            for d in stats
        ],
        "next": (nxt.id if nxt else None),
        "next_challenge": next_challenge_payload(engine),
    }
