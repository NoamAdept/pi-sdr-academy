"""Curriculum admin: validate drafts, create challenge stubs, save proposals."""

from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .dojos import load_dojos
from .engine import AcademyEngine
from .models import Challenge, Module, load_yaml

CHALLENGE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)+$")
MODULE_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DIFFICULTIES = {"easy", "medium", "hard"}
VALIDATIONS = {"exact", "regex", "case_insensitive", "script", "session"}
ENV_TYPES = {"workspace", "service", "iq", "flowgraph", "mixed"}


def admin_enabled() -> bool:
    return os.environ.get("ACADEMY_ADMIN", "").strip().lower() in ("1", "true", "yes")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "new-challenge"


def suggest_challenge_id(module_slug: str, title: str) -> str:
    prefix = module_slug.split("-")[0][:12]
    base = slugify(title)
    if base.startswith(f"{prefix}-"):
        return base
    return f"{prefix}-{base}" if prefix else base


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )


def validate_challenge_draft(data: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors (empty list = ok)."""
    errors: list[str] = []

    for field in (
        "id",
        "module",
        "title",
        "difficulty",
        "estimated_time",
        "description",
        "solution",
        "explanation",
    ):
        if not str(data.get(field, "")).strip():
            errors.append(f"Missing required field: {field}")

    cid = str(data.get("id", "")).strip()
    if cid and not CHALLENGE_ID_RE.fullmatch(cid):
        errors.append("Challenge id must be kebab-case (e.g. orient-find-flag).")

    module = str(data.get("module", "")).strip()
    if module and not MODULE_SLUG_RE.fullmatch(module):
        errors.append("Module slug must be lowercase kebab-case.")

    difficulty = str(data.get("difficulty", "")).strip()
    if difficulty and difficulty not in DIFFICULTIES:
        errors.append(f"Difficulty must be one of: {', '.join(sorted(DIFFICULTIES))}.")

    objectives = data.get("objectives") or []
    if not isinstance(objectives, list) or not objectives:
        errors.append("Add at least one learning objective.")

    hints = data.get("hints") or []
    if not isinstance(hints, list) or len(hints) < 2:
        errors.append("Add at least two hints (level + text).")
    else:
        for idx, hint in enumerate(hints, start=1):
            if not isinstance(hint, dict):
                errors.append(f"Hint {idx} must be an object.")
                continue
            if not str(hint.get("text", "")).strip():
                errors.append(f"Hint {idx} is missing text.")
            level = hint.get("level")
            if not isinstance(level, int) or level < 1:
                errors.append(f"Hint {idx} needs a level >= 1.")

    flags = data.get("flags") or {}
    if not isinstance(flags, dict):
        errors.append("flags must be an object.")
    else:
        if not str(flags.get("value", "")).strip():
            errors.append("Flag value template is required.")
        validation = str(flags.get("validation", "session")).strip()
        if validation not in VALIDATIONS:
            errors.append(f"Flag validation must be one of: {', '.join(sorted(VALIDATIONS))}.")

    environment = data.get("environment") or {"type": "workspace"}
    if not isinstance(environment, dict):
        errors.append("environment must be an object.")
    else:
        env_type = str(environment.get("type", "workspace")).strip()
        if env_type not in ENV_TYPES:
            errors.append(f"environment.type must be one of: {', '.join(sorted(ENV_TYPES))}.")

    files = data.get("files") or []
    if not isinstance(files, list) or not files:
        errors.append("List at least one staged file (usually README.txt).")

    return errors


def build_challenge_yaml(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize a draft into a schema-shaped challenge mapping."""
    hints = []
    for idx, hint in enumerate(data.get("hints") or [], start=1):
        if not isinstance(hint, dict):
            continue
        level = hint.get("level")
        if not isinstance(level, int):
            level = idx
        hints.append({"level": level, "text": str(hint.get("text", "")).rstrip() + "\n"})

    flags_raw = data.get("flags") or {}
    flags: dict[str, Any] = {
        "value": str(flags_raw.get("value", "")).strip(),
        "validation": str(flags_raw.get("validation", "session")).strip() or "session",
    }
    for key in ("pattern", "script"):
        if flags_raw.get(key):
            flags[key] = str(flags_raw[key]).strip()
    plant_files = flags_raw.get("plant_files") or []
    if plant_files:
        flags["plant_files"] = list(plant_files)

    environment = dict(data.get("environment") or {"type": "workspace"})
    if "type" not in environment:
        environment["type"] = "workspace"

    payload: dict[str, Any] = {
        "id": str(data["id"]).strip(),
        "module": str(data["module"]).strip(),
        "title": str(data["title"]).strip(),
        "difficulty": str(data["difficulty"]).strip(),
        "estimated_time": str(data["estimated_time"]).strip(),
        "prerequisites": list(data.get("prerequisites") or []),
        "objectives": list(data.get("objectives") or []),
        "description": str(data["description"]).rstrip() + "\n",
        "environment": environment,
        "files": list(data.get("files") or ["README.txt"]),
        "expected_tools": list(data.get("expected_tools") or []),
        "flags": flags,
        "hints": hints,
        "solution": str(data.get("solution", "")).rstrip() + "\n",
        "explanation": str(data.get("explanation", "")).rstrip() + "\n",
    }

    mastery = data.get("mastery_evidence") or []
    if mastery:
        payload["mastery_evidence"] = list(mastery)

    extension = data.get("extension")
    if isinstance(extension, dict) and extension:
        payload["extension"] = extension

    performance_notes = data.get("performance_notes")
    if performance_notes:
        payload["performance_notes"] = str(performance_notes).rstrip() + "\n"

    optional_hardware = data.get("optional_hardware") or []
    if optional_hardware:
        payload["optional_hardware"] = list(optional_hardware)

    return payload


def curriculum_overview(engine: AcademyEngine) -> dict[str, Any]:
    dojos = load_dojos(engine.curriculum_root)
    modules_by_slug = {m.slug: m for m in engine.modules}
    dojo_rows = []
    seen: set[str] = set()

    for dojo in dojos.all:
        mod_rows = []
        for slug in dojo.modules:
            seen.add(slug)
            module = modules_by_slug.get(slug)
            if module is None:
                mod_rows.append({"slug": slug, "title": slug, "missing": True, "challenges": []})
                continue
            chs = engine.module_challenges(slug)
            mod_rows.append(
                {
                    "slug": module.slug,
                    "title": module.title,
                    "order": module.order,
                    "description": module.description.strip(),
                    "challenge_count": len(chs),
                    "challenges": [{"id": c.id, "title": c.title, "difficulty": c.difficulty} for c in chs],
                    "path": str(module.path) if module.path else None,
                }
            )
        dojo_rows.append(
            {
                "id": dojo.id,
                "title": dojo.title,
                "belt": dojo.belt,
                "kind": dojo.kind,
                "modules": mod_rows,
            }
        )

    unassigned = []
    for module in engine.modules:
        if module.slug not in seen:
            chs = engine.module_challenges(module.slug)
            unassigned.append(
                {
                    "slug": module.slug,
                    "title": module.title,
                    "order": module.order,
                    "challenge_count": len(chs),
                }
            )

    return {
        "admin_enabled": admin_enabled(),
        "curriculum_root": str(engine.curriculum_root),
        "module_count": len(engine.modules),
        "challenge_count": len(engine.challenges),
        "dojos": dojo_rows,
        "unassigned_modules": unassigned,
        "modules": [
            {
                "slug": m.slug,
                "title": m.title,
                "order": m.order,
                "challenge_count": len(engine.module_challenges(m.slug)),
                "path": str(m.path) if m.path else None,
            }
            for m in engine.modules
        ],
    }


def module_detail(engine: AcademyEngine, slug: str) -> dict[str, Any] | None:
    try:
        module = engine.get_module(slug)
    except KeyError:
        return None
    challenges = engine.module_challenges(slug)
    return {
        "slug": module.slug,
        "title": module.title,
        "order": module.order,
        "description": module.description.strip(),
        "prerequisites": module.prerequisites,
        "challenges": [
            {
                "id": c.id,
                "title": c.title,
                "difficulty": c.difficulty,
                "estimated_time": c.estimated_time,
            }
            for c in challenges
        ],
        "registered_ids": list(module.challenges),
        "path": str(module.path) if module.path else None,
    }


def _module_path_for_slug(engine: AcademyEngine, slug: str) -> Path | None:
    for module in engine.modules:
        if module.slug == slug and module.path:
            return module.path
    return None


def _readme_from_description(description: str, title: str) -> str:
    lines = [f"# {title}", ""]
    for raw in description.strip().splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            continue
        lines.append(line)
    lines.extend(
        [
            "",
            "---",
            "",
            "When you have the flag:",
            "",
            "  academy submit 'flag{...}'",
            "",
            "Or run the checker if one is provided:",
            "",
            "  ./check",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def create_challenge(
    engine: AcademyEngine,
    data: dict[str, Any],
    *,
    register_in_module: bool = True,
    write_readme: bool = True,
) -> dict[str, Any]:
    payload = build_challenge_yaml(data)
    errors = validate_challenge_draft(payload)
    if errors:
        return {"ok": False, "errors": errors}

    cid = payload["id"]
    module_slug = payload["module"]
    if cid in engine._challenges:
        return {"ok": False, "errors": [f"Challenge already exists: {cid}"]}

    module_path = _module_path_for_slug(engine, module_slug)
    if module_path is None:
        return {"ok": False, "errors": [f"Unknown module slug: {module_slug}"]}

    challenge_dir = module_path / "challenges" / cid
    if challenge_dir.exists():
        return {"ok": False, "errors": [f"Challenge directory already exists: {challenge_dir}"]}

    files_dir = challenge_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=False)
    yaml_path = challenge_dir / "challenge.yaml"
    yaml_path.write_text(dump_yaml(payload), encoding="utf-8")

    if write_readme and "README.txt" in payload["files"]:
        readme = _readme_from_description(payload["description"], payload["title"])
        (files_dir / "README.txt").write_text(readme, encoding="utf-8")

    module_yaml = module_path / "module.yaml"
    module_data = load_yaml(module_yaml)
    registered = list(module_data.get("challenges") or [])
    if register_in_module and cid not in registered:
        registered.append(cid)
        module_data["challenges"] = registered
        module_yaml.write_text(dump_yaml(module_data), encoding="utf-8")

    engine.reload()
    return {
        "ok": True,
        "challenge_id": cid,
        "module": module_slug,
        "paths": {
            "challenge_dir": str(challenge_dir),
            "challenge_yaml": str(yaml_path),
            "files_dir": str(files_dir),
        },
        "registered_in_module": register_in_module and cid in registered,
        "next_steps": [
            f"Add puzzle files under {files_dir}/",
            "Add a checker (files/check or files/checker.py) if needed.",
            "Run make test and play the challenge from the dojo.",
        ],
    }


def proposals_dir(curriculum_root: Path) -> Path:
    return Path(curriculum_root) / "proposals"


def save_proposal(
    curriculum_root: Path,
    *,
    kind: str,
    title: str,
    body: dict[str, Any],
    notes: str = "",
) -> dict[str, Any]:
    """Persist a curriculum suggestion for later review."""
    root = proposals_dir(curriculum_root)
    root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = slugify(title)[:48]
    filename = f"{stamp}-{slug}.yaml"
    path = root / filename
    payload = {
        "kind": kind,
        "title": title,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": notes.strip(),
        **body,
    }
    path.write_text(dump_yaml(payload), encoding="utf-8")
    return {"ok": True, "path": str(path), "filename": filename}


def list_proposals(curriculum_root: Path) -> list[dict[str, Any]]:
    root = proposals_dir(curriculum_root)
    if not root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.yaml"), reverse=True):
        try:
            data = load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue
        rows.append(
            {
                "filename": path.name,
                "path": str(path),
                "kind": data.get("kind", "unknown"),
                "title": data.get("title", path.stem),
                "status": data.get("status", "pending"),
                "created_at": data.get("created_at"),
                "notes": data.get("notes", ""),
            }
        )
    return rows


def apply_proposal(engine: AcademyEngine, filename: str) -> dict[str, Any]:
    path = proposals_dir(engine.curriculum_root) / filename
    if not path.is_file():
        return {"ok": False, "error": "Proposal not found"}

    data = load_yaml(path)
    kind = str(data.get("kind", "")).strip()

    if kind == "challenge":
        challenge = data.get("challenge")
        if not isinstance(challenge, dict):
            return {"ok": False, "error": "Proposal missing challenge object"}
        result = create_challenge(engine, challenge, register_in_module=True)
        if result.get("ok"):
            data["status"] = "applied"
            data["applied_at"] = datetime.now(timezone.utc).isoformat()
            path.write_text(dump_yaml(data), encoding="utf-8")
        return result

    if kind == "module":
        return {
            "ok": False,
            "error": "Module proposals must be applied manually (create module.yaml + dojos.yaml edits).",
            "proposal": data,
        }

    if kind == "curriculum_note":
        return {
            "ok": True,
            "applied": False,
            "message": "Curriculum note saved for review; no automatic changes.",
        }

    return {"ok": False, "error": f"Unknown proposal kind: {kind}"}


def default_challenge_draft(module_slug: str, title: str = "") -> dict[str, Any]:
    title = title.strip() or "New Challenge"
    cid = suggest_challenge_id(module_slug, title)
    prefix = cid.replace("-", "_")
    return {
        "id": cid,
        "module": module_slug,
        "title": title,
        "difficulty": "easy",
        "estimated_time": "30-60 minutes",
        "prerequisites": [],
        "objectives": ["describe_skill_here"],
        "description": (
            "Describe what the student should do.\n\n"
            "Keep instructions in README.txt and reference commands they should try.\n"
        ),
        "environment": {"type": "workspace", "notes": "Offline workspace challenge."},
        "files": ["README.txt"],
        "expected_tools": [],
        "flags": {
            "value": f"flag{{{prefix}_template}}",
            "validation": "session",
        },
        "hints": [
            {"level": 1, "text": "Start by reading README.txt and listing the workspace."},
            {"level": 2, "text": "Look for files or patterns that stand out."},
        ],
        "solution": "Document the instructor walkthrough here.\n",
        "explanation": "Explain the concept students should take away.\n",
    }
