"""Challenge engine: load curriculum, stage workspaces, track progress."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable

from .models import Challenge, Module, load_yaml
from .paths import resolve_flag_path, resolve_workspace
from .progress import ProgressRepository, ProgressStore
from .secrets import (
    mint_session_flag,
    normalize_answer,
    save_session_secret,
)
from .validation import validate_challenge_flag


class AcademyEngine:
    def __init__(
        self,
        curriculum_root: Path,
        data_dir: Path,
        workspace_root: Path | None = None,
    ):
        self.curriculum_root = Path(curriculum_root)
        self.data_dir = Path(data_dir)
        self.workspace_root = Path(workspace_root) if workspace_root else resolve_workspace()
        self.flag_path = resolve_flag_path()
        self.modules_dir = self.curriculum_root / "modules"
        self.progress_repo = ProgressRepository(self.data_dir / "progress.json")
        self._modules: dict[str, Module] = {}
        self._challenges: dict[str, Challenge] = {}
        self.reload()

    def reload(self) -> None:
        self._modules.clear()
        self._challenges.clear()
        if not self.modules_dir.exists():
            return
        for module_path in sorted(self.modules_dir.iterdir()):
            meta = module_path / "module.yaml"
            if not meta.exists():
                continue
            module = Module.from_dict(load_yaml(meta), path=module_path)
            self._modules[module.slug] = module
            challenges_root = module_path / "challenges"
            if not challenges_root.exists():
                continue
            for challenge_dir in sorted(challenges_root.iterdir()):
                ch_file = challenge_dir / "challenge.yaml"
                if not ch_file.exists():
                    continue
                challenge = Challenge.from_dict(load_yaml(ch_file), path=ch_file)
                self._challenges[challenge.id] = challenge

    @property
    def modules(self) -> list[Module]:
        return sorted(self._modules.values(), key=lambda m: m.order)

    @property
    def challenges(self) -> list[Challenge]:
        return list(self._challenges.values())

    def get_module(self, slug: str) -> Module:
        if slug not in self._modules:
            raise KeyError(f"Unknown module: {slug}")
        return self._modules[slug]

    def get_challenge(self, challenge_id: str) -> Challenge:
        if challenge_id not in self._challenges:
            raise KeyError(f"Unknown challenge: {challenge_id}")
        return self._challenges[challenge_id]

    def module_challenges(self, slug: str) -> list[Challenge]:
        module = self.get_module(slug)
        result: list[Challenge] = []
        for cid in module.challenges:
            if cid in self._challenges:
                result.append(self._challenges[cid])
        # Fallback: discover by module field
        if not result:
            result = [c for c in self._challenges.values() if c.module == slug]
            order = {"easy": 0, "medium": 1, "hard": 2}
            result.sort(key=lambda c: (order.get(c.difficulty, 9), c.id))
        return result

    def progress(self) -> ProgressStore:
        return self.progress_repo.load()

    def prerequisites_met(self, challenge: Challenge, store: ProgressStore | None = None) -> bool:
        store = store or self.progress()
        for prereq in challenge.prerequisites:
            # Topic tags are soft; challenge IDs are hard requirements when known
            if prereq in self._challenges:
                prog = store.challenges.get(prereq)
                if not prog or not prog.solved:
                    return False
        return True

    def ordered_challenges(self) -> list[Challenge]:
        """Curriculum order: module order, then listed challenge order."""
        result: list[Challenge] = []
        for module in self.modules:
            result.extend(self.module_challenges(module.slug))
        return result

    def is_solved(self, challenge_id: str, store: ProgressStore | None = None) -> bool:
        store = store or self.progress()
        prog = store.challenges.get(challenge_id)
        return bool(prog and prog.solved)

    def next_available_challenge(self) -> Challenge | None:
        """First unsolved challenge in an unlocked core dojo (else any unmet prereqs)."""
        from .dojos import dojo_stats

        store = self.progress()
        unlocked_modules: set[str] | None = None
        try:
            unlocked_modules = set()
            for d in dojo_stats(self, store):
                if d.kind == "core" and not d.locked:
                    unlocked_modules.update(d.module_slugs)
                if d.kind == "side":
                    unlocked_modules.update(d.module_slugs)
        except Exception:  # noqa: BLE001 — dojos optional
            unlocked_modules = None

        for challenge in self.ordered_challenges():
            if self.is_solved(challenge.id, store):
                continue
            if not self.prerequisites_met(challenge, store):
                continue
            if unlocked_modules is not None:
                # Map challenge.module field (may be slug-ish) onto module slugs
                mod = challenge.module
                # Prefer module membership via engine listing
                in_unlocked = False
                for slug in unlocked_modules:
                    try:
                        if any(c.id == challenge.id for c in self.module_challenges(slug)):
                            in_unlocked = True
                            break
                    except KeyError:
                        continue
                if not in_unlocked and mod not in unlocked_modules:
                    continue
            return challenge
        return None

    def current_challenge(self) -> Challenge | None:
        store = self.progress()
        cid = store.current_challenge_id
        if not cid or cid not in self._challenges:
            return None
        return self._challenges[cid]

    def workspace_for(self, challenge: Challenge | None = None) -> Path:
        """Always the same folder — starting a challenge reloads files here."""
        return self.workspace_root

    def start_challenge(self, challenge_id: str, *, reset: bool = True) -> Path:
        challenge = self.get_challenge(challenge_id)
        store = self.progress()
        if not self.prerequisites_met(challenge, store):
            missing = []
            for p in challenge.prerequisites:
                if p in self._challenges:
                    prog = store.challenges.get(p)
                    if not prog or not prog.solved:
                        missing.append(p)
            raise RuntimeError(
                "Prerequisites not met. Solve these first:\n  - " + "\n  - ".join(missing)
            )

        dest = self.workspace_root
        self.flag_path = resolve_flag_path()
        if reset and dest.exists():
            # Clear previous challenge files; keep the same directory path.
            for child in dest.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        dest.mkdir(parents=True, exist_ok=True)

        src_files = challenge.path.parent / "files" if challenge.path else None
        if src_files and src_files.exists():
            for path in src_files.rglob("*"):
                if path.is_file():
                    rel = path.relative_to(src_files)
                    target = dest / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    _copy_challenge_file(path, target)

        (dest / ".challenge").write_text(challenge.id + "\n", encoding="utf-8")
        (dest / ".flagpath").write_text(str(self.flag_path) + "\n", encoding="utf-8")

        # Mint a fresh randomized submit-flag; keep curriculum template as checker answer.
        answer = normalize_answer(challenge.flags.value)
        session_flag = mint_session_flag(challenge.id, challenge.flags.value)
        save_session_secret(
            self.data_dir,
            challenge.id,
            flag=session_flag,
            answer=answer,
        )

        # Flag file must not contain the answer until academy verify awards it.
        try:
            if self.flag_path.exists():
                self.flag_path.unlink()
            self.flag_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        # Plant the session flag into puzzle files (find / service / env style).
        for rel in challenge.flags.plant_files:
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = None
            if target.exists():
                mode = target.stat().st_mode
                try:
                    target.chmod(mode | 0o600)
                except OSError:
                    pass
            _plant_session_flag(target, session_flag)
            if mode is not None:
                try:
                    target.chmod(mode)
                except OSError:
                    pass

        setup = challenge.path.parent / "setup.sh" if challenge.path else None
        if setup and setup.exists():
            import subprocess

            env = os.environ.copy()
            env["ACADEMY_FLAG_PATH"] = str(self.flag_path)
            env["ACADEMY_WORKSPACE"] = str(dest)
            env["ACADEMY_DATA"] = str(self.data_dir)
            # Setup may plant artifacts; do not export the flag to the student shell.
            result = subprocess.run(
                ["bash", str(setup), str(dest)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"Challenge setup failed:\n{result.stdout}\n{result.stderr}"
                )

        store.start(challenge_id, workspace=str(dest))
        self.progress_repo.save(store)

        current_link = self.data_dir / "current_workspace"
        current_link.write_text(str(dest) + "\n", encoding="utf-8")
        return dest

    def get_hint(self, challenge_id: str) -> tuple[int, str | None]:
        challenge = self.get_challenge(challenge_id)
        store = self.progress()
        store.start(challenge_id, workspace=store.current_workspace)
        level = store.reveal_hint(challenge_id, len(challenge.hints))
        self.progress_repo.save(store)
        for hint in sorted(challenge.hints, key=lambda h: h.level):
            if hint.level == level:
                return level, hint.text
        if challenge.hints:
            last = max(challenge.hints, key=lambda h: h.level)
            return last.level, last.text
        return 0, None

    def list_revealed_hints(self, challenge_id: str) -> list[tuple[int, str]]:
        challenge = self.get_challenge(challenge_id)
        store = self.progress()
        prog = store.ensure(challenge_id)
        revealed = []
        for hint in sorted(challenge.hints, key=lambda h: h.level):
            if hint.level <= prog.hints_revealed:
                revealed.append((hint.level, hint.text))
        return revealed

    def submit(self, challenge_id: str, flag: str) -> bool:
        challenge = self.get_challenge(challenge_id)
        ok = validate_challenge_flag(challenge, flag, data_dir=self.data_dir)
        store = self.progress()
        store.record_attempt(challenge_id, ok)
        self.progress_repo.save(store)
        return ok

    def status_summary(self) -> dict:
        store = self.progress()
        total = len(self._challenges)
        solved = sum(1 for c in store.challenges.values() if c.solved)
        by_module = {}
        for module in self.modules:
            chs = self.module_challenges(module.slug)
            m_solved = sum(
                1 for c in chs if store.challenges.get(c.id) and store.challenges[c.id].solved
            )
            by_module[module.slug] = {
                "title": module.title,
                "solved": m_solved,
                "total": len(chs),
            }
        return {
            "solved": solved,
            "total": total,
            "modules": by_module,
            "current_challenge_id": store.current_challenge_id,
            "current_workspace": store.current_workspace,
        }

    def iter_challenge_paths(self) -> Iterable[Path]:
        for challenge in self._challenges.values():
            if challenge.path:
                yield challenge.path


def _allowed_session_flag_plant(target: Path) -> bool:
    """Live flags may only land in intentional flag/secret files — never scripts."""
    name = target.name
    if name == "lab_shell.sh":
        return True
    if name in {".beacon_secret", ".relay_secret", ".lab_env", "flag.txt"}:
        return True
    if name.endswith(".flag"):
        return True
    return False


def _plant_session_flag(target: Path, flag: str) -> None:
    """Write/replace flag text in a planted puzzle file without leaking via checkers."""
    import re

    name = target.name
    if not _allowed_session_flag_plant(target):
        raise RuntimeError(
            f"Refusing to plant session flag into {target.name!r}; "
            "use a one-shot secret or flag file (e.g. .beacon_secret, flag.txt)"
        )

    if target.exists() and target.is_file():
        try:
            text = target.read_text(encoding="utf-8")
        except OSError:
            text = ""
        # Environment challenge: never leave the live flag inside lab_shell.sh
        # (students could `cat` it). Plant a one-shot .lab_env instead.
        if name == "lab_shell.sh":
            mid = max(1, len(flag) // 2)
            part1, part2 = flag[:mid], flag[mid:]
            env_path = target.parent / ".lab_env"
            env_path.write_text(
                f"export LAB_FLAG_PART1={part1!r}\nexport LAB_FLAG_PART2={part2!r}\n",
                encoding="utf-8",
            )
            try:
                os.chmod(env_path, 0o600)
            except OSError:
                pass
            text = re.sub(
                r"export LAB_FLAG_PART1=.*",
                "unset LAB_FLAG_PART1 2>/dev/null || true",
                text,
            )
            text = re.sub(
                r"export LAB_FLAG_PART2=.*",
                "unset LAB_FLAG_PART2 2>/dev/null || true",
                text,
            )
            text = re.sub(
                r"export DECOY_FLAG=.*",
                "export DECOY_FLAG='flag{wrong_source_use_lab_vars}'",
                text,
            )
            target.write_text(text, encoding="utf-8")
            return
        if re.search(r"flag\{[^}]+\}", text):
            # Prefer replacing the curriculum template / known payload keys first.
            if '"flag"' in text or "'flag'" in text:
                text = re.sub(
                    r'(["\']flag["\']\s*:\s*)["\']flag\{[^}]+\}["\']',
                    rf'\1"{flag}"',
                    text,
                )
            text = re.sub(r"flag\{[^}]+\}", flag, text)
            # Restore intentional decoys if we wiped them
            if name in {"decoy.env", "lab_shell.sh"} and "wrong_source" not in text:
                pass
            target.write_text(text, encoding="utf-8")
            return
    target.write_text(flag + "\n", encoding="utf-8")


def _copy_challenge_file(src: Path, dst: Path) -> None:
    """Copy a starter file, preserving mode even when source is mode 000."""
    mode = src.stat().st_mode
    restored = False
    if not os.access(src, os.R_OK):
        src.chmod(mode | 0o400)
        restored = True
    try:
        shutil.copyfile(src, dst)
    finally:
        if restored:
            src.chmod(mode)
    os.chmod(dst, mode)

