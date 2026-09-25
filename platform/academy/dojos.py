"""Dojos + belt progression (pwn.college-inspired curriculum map)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from .engine import AcademyEngine
from .progress import ProgressStore
from .ui_flavor import display_title


BELT_COLORS = {
    "white": "#E8EDF5",
    "yellow": "#E9C46A",  # amber vertex
    "orange": "#E76F51",  # coral vertex
    "green": "#2A9D8F",   # teal vertex
    "blue": "#6C7AE0",    # indigo vertex
    "purple": "#6C7AE0",
    "brown": "#8B95A8",
    "black": "#0E1218",
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

    # Strip decorative ==== underlines left after title removal
    if lines and set(lines[0].strip()) <= {"=", "-", "*"} and len(lines[0].strip()) >= 3:
        lines = lines[1:]
        while lines and lines[0] == "":
            lines.pop(0)

    steps: list[str] = []
    mission_parts: list[str] = []
    in_workflow = False
    skip_cmd_block = False
    for line in lines:
        low = line.lower().rstrip(":")
        # Skip stock workspace boilerplate — confuses people before Start
        if "already in the challenge folder" in low:
            continue
        if low in {"goal", "mission", "task", "what is this?", "what is this"}:
            in_workflow = False
            skip_cmd_block = False
            continue
        if low in {"workflow", "steps", "what to do"} or low.startswith("workflow"):
            in_workflow = True
            skip_cmd_block = False
            continue
        if in_workflow:
            step = line.lstrip("0123456789.-) ").strip()
            if not step:
                continue
            # Skip bare shell crumbs — keep human instructions only
            toks = step.replace("`", "").split()
            cmd = toks[0] if toks else ""
            if (
                "academy" in step.lower()
                or "flagpath" in step.lower()
                or cmd.startswith("./")
                or cmd in {
                    "ls", "pwd", "cat", "find", "chmod", "ps", "curl",
                    "printenv", "printf", "exit", "cd", "grep",
                }
            ):
                continue
            if len(step) < 90:
                steps.append(step)
            continue

        # Skip fenced-looking command-only blocks from READMEs (indented tool lists)
        if line.startswith("  ") or (
            len(line.split()) <= 4
            and all(tok.startswith((".", "/", "`")) or tok in {"pwd", "ls", "cd", "find", "cat", "FILE", "-la", "-type", "f"} for tok in line.replace("`", "").split())
        ):
            continue

        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            if heading in {"mission", "task", "goal", "what is this?", "what is this"}:
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
                "keep the quotes",
                "back in the challenge folder, write the flag",
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
    mission = mission.rstrip(":").rstrip()
    for tail in ("Explore with", "Use", "Tools", "Try"):
        if mission.lower().endswith(tail.lower()):
            mission = mission[: -len(tail)].rstrip(" :")
            break

    # One or two sentences — instant clarity
    sentences = [
        s.strip()
        for s in mission.replace("?", "?|").replace("!", "!|").replace(". ", ".|").split("|")
        if s.strip()
    ]
    mission = " ".join(sentences[:2]).strip()
    if len(mission) > 220:
        mission = mission[:217].rstrip() + "…"

    blurb = sentences[0].strip() if sentences else (challenge.title or challenge.id or "Challenge")
    if blurb and not blurb.endswith((".", "!", "?")):
        blurb += "."
    if len(blurb) > 160:
        blurb = blurb[:157].rstrip() + "…"

    clean_steps: list[str] = []
    for step in steps[:4]:
        s = " ".join(step.replace("`", "").split())
        if "academy" in s.lower() or "flagpath" in s.lower():
            continue
        if len(s) > 90:
            s = s[:87].rstrip() + "…"
        clean_steps.append(s)

    if not clean_steps:
        clean_steps = [
            "Press Start",
            "Open the challenge folder → read README.txt",
            "Press Done when finished",
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


def _dojo_contents_preview(engine: AcademyEngine, module_slugs: list[str]) -> list[dict[str, Any]]:
    """Module titles + challenge titles so belts can be browsed from the catalog."""
    out: list[dict[str, Any]] = []
    for slug in module_slugs:
        try:
            module = engine.get_module(slug)
        except KeyError:
            continue
        challenges = [
            {
                "id": c.id,
                "title": display_title(c.id, c.title),
                "difficulty": c.difficulty,
            }
            for c in engine.module_challenges(slug)
        ]
        out.append(
            {
                "slug": module.slug,
                "title": module.title,
                "description": (module.description or "").strip(),
                "challenges": challenges,
                "challenge_count": len(challenges),
            }
        )
    return out


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
                "contents": _dojo_contents_preview(engine, d.module_slugs),
            }
            for d in stats
        ],
        "next": (nxt.id if nxt else None),
        "next_challenge": next_challenge_payload(engine),
    }


def _day_key(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()


def _streak(days: dict[str, int], today: date | None = None) -> int:
    """Consecutive days with ≥1 solve, ending today or yesterday."""
    today = today or datetime.now(tz=timezone.utc).date()
    cursor = today
    if days.get(cursor.isoformat(), 0) <= 0:
        cursor = today - timedelta(days=1)
        if days.get(cursor.isoformat(), 0) <= 0:
            return 0
    streak = 0
    while days.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def profile_payload(engine: AcademyEngine) -> dict[str, Any]:
    """Operator profile: solve calendar + belt mountain progress."""
    store = engine.progress()
    summary = engine.status_summary()
    stats = [d for d in dojo_stats(engine, store) if d.kind == "core"]

    cid_to_belt: dict[str, tuple[str, str]] = {}
    for d in stats:
        for slug in d.module_slugs:
            try:
                for c in engine.module_challenges(slug):
                    cid_to_belt[c.id] = (d.belt, d.belt_label)
            except KeyError:
                continue

    day_counts: dict[str, int] = {}
    recent: list[dict[str, Any]] = []
    for cid, prog in store.challenges.items():
        if not prog.solved:
            continue
        ts = prog.completed_at or prog.started_at
        if ts:
            key = _day_key(ts)
            day_counts[key] = day_counts.get(key, 0) + 1
        belt, belt_label = cid_to_belt.get(cid, ("", ""))
        try:
            ch = engine.get_challenge(cid)
            title = display_title(cid, ch.title)
        except KeyError:
            title = cid
        recent.append(
            {
                "id": cid,
                "title": title,
                "completed_at": prog.completed_at or prog.started_at,
                "belt": belt,
                "belt_label": belt_label,
            }
        )

    recent.sort(key=lambda r: r["completed_at"] or 0, reverse=True)

    # Fractional ascent: each core belt is an equal terrace on the mountain.
    n_belts = max(1, len(stats))
    ascent = 0.0
    current_belt = stats[0].belt if stats else "white"
    current_set = False
    for i, d in enumerate(stats):
        frac = (d.solved / d.challenges) if d.challenges else 0.0
        ascent += frac / n_belts
        if not current_set and d.solved < d.challenges:
            current_belt = d.belt
            current_set = True
        elif not current_set and i == len(stats) - 1 and d.challenges and d.solved >= d.challenges:
            current_belt = d.belt
            current_set = True

    best_day = None
    if day_counts:
        best_key = max(day_counts, key=lambda k: (day_counts[k], k))
        best_day = {"date": best_key, "count": day_counts[best_key]}

    return {
        "solved": summary["solved"],
        "total": summary["total"],
        "streak": _streak(day_counts),
        "best_day": best_day,
        "days": day_counts,
        "belts": [
            {
                "id": d.id,
                "title": d.title,
                "belt": d.belt,
                "belt_label": d.belt_label,
                "belt_color": d.belt_color,
                "tagline": d.tagline,
                "solved": d.solved,
                "challenges": d.challenges,
                "complete": d.challenges > 0 and d.solved >= d.challenges,
                "locked": d.locked,
            }
            for d in stats
        ],
        "recent": recent[:12],
        "current_belt": current_belt,
        "ascent_pct": round(100 * min(1.0, ascent), 1),
    }
