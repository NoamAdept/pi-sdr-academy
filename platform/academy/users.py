"""Local user registry for closed-network labs."""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

USER_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")
ROLES = {"student", "instructor"}


def slugify_user_id(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-_")
    if text and text[0].isdigit():
        text = f"u-{text}"
    return text[:32] or "user"


@dataclass
class User:
    id: str
    display_name: str
    role: str = "student"
    active: bool = True
    created_at: float = field(default_factory=time.time)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        return cls(
            id=str(data.get("id", "")).strip(),
            display_name=str(data.get("display_name") or data.get("id") or "").strip(),
            role=str(data.get("role") or "student").strip() or "student",
            active=bool(data.get("active", True)),
            created_at=float(data.get("created_at") or time.time()),
            notes=str(data.get("notes") or ""),
        )


class UserRegistry:
    """JSON user directory under the academy data dir."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, User]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        users: dict[str, User] = {}
        for row in raw.get("users") or []:
            if not isinstance(row, dict):
                continue
            user = User.from_dict(row)
            if user.id:
                users[user.id] = user
        return users

    def save(self, users: dict[str, User]) -> None:
        payload = {
            "users": [u.to_dict() for u in sorted(users.values(), key=lambda u: u.id)],
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def list_users(self, *, active_only: bool = False) -> list[User]:
        users = self.load()
        rows = list(users.values())
        if active_only:
            rows = [u for u in rows if u.active]
        rows.sort(key=lambda u: (not u.active, u.display_name.lower(), u.id))
        return rows

    def get(self, user_id: str) -> User | None:
        return self.load().get(user_id)

    def upsert(
        self,
        *,
        user_id: str,
        display_name: str,
        role: str = "student",
        active: bool = True,
        notes: str = "",
    ) -> User:
        uid = slugify_user_id(user_id)
        if not USER_ID_RE.fullmatch(uid):
            raise ValueError(
                "User id must be 2–32 chars: start with a letter, then a-z 0-9 _ -"
            )
        role = role if role in ROLES else "student"
        users = self.load()
        existing = users.get(uid)
        user = User(
            id=uid,
            display_name=(display_name or uid).strip()[:64],
            role=role,
            active=active,
            created_at=existing.created_at if existing else time.time(),
            notes=(notes or "").strip()[:240],
        )
        users[uid] = user
        self.save(users)
        return user

    def set_active(self, user_id: str, active: bool) -> User | None:
        users = self.load()
        user = users.get(user_id)
        if not user:
            return None
        user.active = active
        users[user_id] = user
        self.save(users)
        return user

    def ensure_local_default(self) -> User:
        """Guarantee a default operator exists for single-machine labs."""
        users = self.load()
        if users:
            for u in users.values():
                if u.active:
                    return u
            return next(iter(users.values()))
        return self.upsert(user_id="local", display_name="Local Operator", role="instructor")
