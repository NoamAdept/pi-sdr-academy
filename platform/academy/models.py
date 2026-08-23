"""Data models for challenges, modules, and student progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Hint:
    level: int
    text: str


@dataclass
class FlagSpec:
    value: str
    validation: str = "session"
    pattern: str | None = None
    script: str | None = None
    plant_files: list[str] = field(default_factory=list)


@dataclass
class Challenge:
    id: str
    module: str
    title: str
    difficulty: str
    estimated_time: str
    prerequisites: list[str]
    objectives: list[str]
    description: str
    environment: dict[str, Any]
    files: list[str]
    expected_tools: list[str]
    flags: FlagSpec
    hints: list[Hint]
    solution: str
    explanation: str
    mastery_evidence: list[str] = field(default_factory=list)
    extension: dict[str, Any] | None = None
    performance_notes: str | None = None
    optional_hardware: list[str] = field(default_factory=list)
    path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: Path | None = None) -> Challenge:
        flag_raw = data["flags"]
        hints = [Hint(level=h["level"], text=h["text"]) for h in data.get("hints", [])]
        return cls(
            id=data["id"],
            module=data["module"],
            title=data["title"],
            difficulty=data["difficulty"],
            estimated_time=data["estimated_time"],
            prerequisites=list(data.get("prerequisites", [])),
            objectives=list(data.get("objectives", [])),
            description=data["description"],
            environment=dict(data.get("environment", {"type": "workspace"})),
            files=list(data.get("files", [])),
            expected_tools=list(data.get("expected_tools", [])),
            flags=FlagSpec(
                value=flag_raw["value"],
                validation=flag_raw.get("validation", "session"),
                pattern=flag_raw.get("pattern"),
                script=flag_raw.get("script"),
                plant_files=list(flag_raw.get("plant_files", [])),
            ),
            hints=hints,
            solution=data.get("solution", ""),
            explanation=data.get("explanation", ""),
            mastery_evidence=list(data.get("mastery_evidence", [])),
            extension=data.get("extension"),
            performance_notes=data.get("performance_notes"),
            optional_hardware=list(data.get("optional_hardware", [])),
            path=path,
        )


@dataclass
class Module:
    id: str
    slug: str
    title: str
    order: int
    description: str
    prerequisites: list[str]
    challenges: list[str]
    path: Path | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: Path | None = None) -> Module:
        return cls(
            id=data["id"],
            slug=data["slug"],
            title=data["title"],
            order=int(data["order"]),
            description=data.get("description", ""),
            prerequisites=list(data.get("prerequisites", [])),
            challenges=list(data.get("challenges", [])),
            path=path,
        )


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data
