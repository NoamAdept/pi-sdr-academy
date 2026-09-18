"""Local progress store (JSON on disk). Offline-only."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class ChallengeProgress:
    started_at: float | None = None
    completed_at: float | None = None
    hints_revealed: int = 0
    attempts: int = 0
    solved: bool = False
    notes: str = ""


@dataclass
class ProgressStore:
    student_id: str = "local"
    challenges: dict[str, ChallengeProgress] = field(default_factory=dict)
    mastered_topics: dict[str, list[str]] = field(default_factory=dict)
    current_challenge_id: str | None = None
    current_workspace: str | None = None

    def ensure(self, challenge_id: str) -> ChallengeProgress:
        if challenge_id not in self.challenges:
            self.challenges[challenge_id] = ChallengeProgress()
        return self.challenges[challenge_id]

    def start(self, challenge_id: str, workspace: str | None = None) -> ChallengeProgress:
        prog = self.ensure(challenge_id)
        if prog.started_at is None:
            prog.started_at = time.time()
        self.current_challenge_id = challenge_id
        if workspace is not None:
            self.current_workspace = workspace
        return prog

    def reveal_hint(self, challenge_id: str, max_hints: int) -> int:
        prog = self.ensure(challenge_id)
        if prog.hints_revealed < max_hints:
            prog.hints_revealed += 1
        return prog.hints_revealed

    def record_attempt(self, challenge_id: str, success: bool) -> ChallengeProgress:
        prog = self.ensure(challenge_id)
        prog.attempts += 1
        if success and not prog.solved:
            prog.solved = True
            prog.completed_at = time.time()
        return prog

    def to_dict(self) -> dict[str, Any]:
        return {
            "student_id": self.student_id,
            "challenges": {k: asdict(v) for k, v in self.challenges.items()},
            "mastered_topics": self.mastered_topics,
            "current_challenge_id": self.current_challenge_id,
            "current_workspace": self.current_workspace,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgressStore:
        challenges = {
            cid: ChallengeProgress(**cdata)
            for cid, cdata in data.get("challenges", {}).items()
        }
        return cls(
            student_id=data.get("student_id", "local"),
            challenges=challenges,
            mastered_topics=dict(data.get("mastered_topics", {})),
            current_challenge_id=data.get("current_challenge_id"),
            current_workspace=data.get("current_workspace"),
        )


class ProgressRepository:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> ProgressStore:
        if not self.path.exists():
            return ProgressStore()
        with self.path.open("r", encoding="utf-8") as fh:
            return ProgressStore.from_dict(json.load(fh))

    def save(self, store: ProgressStore) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(store.to_dict(), fh, indent=2, sort_keys=True)
            fh.write("\n")
        tmp.replace(self.path)


class HookedProgressRepository(ProgressRepository):
    """ProgressRepository that runs a callback after each successful save."""

    def __init__(self, path: Path, on_save: Callable[[ProgressStore], None] | None = None):
        super().__init__(path)
        self.on_save = on_save

    def save(self, store: ProgressStore) -> None:
        super().save(store)
        if self.on_save is not None:
            self.on_save(store)
