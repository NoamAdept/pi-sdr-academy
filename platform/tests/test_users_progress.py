"""Tests for users, challenge delete, and git-branch progress."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CURRICULUM = ROOT / "curriculum"


@pytest.fixture()
def engine(tmp_path):
    from academy.engine import AcademyEngine

    return AcademyEngine(
        curriculum_root=CURRICULUM,
        data_dir=tmp_path / "data",
        workspace_root=tmp_path / "workspace",
    )


def test_users_and_per_user_progress_branches(engine):
    alice = engine.users.upsert(user_id="alice", display_name="Alice")
    bob = engine.users.upsert(user_id="bob", display_name="Bob")
    assert alice.id == "alice"

    engine.set_user("alice")
    store = engine.progress()
    from academy.progress import ChallengeProgress

    store.challenges["orient-find-flag"] = ChallengeProgress(
        solved=True, completed_at=100.0, attempts=1
    )
    engine.progress_repo.save(store)

    engine.set_user("bob")
    assert engine.progress().challenges.get("orient-find-flag") is None

    engine.set_user("alice")
    assert engine.progress().challenges["orient-find-flag"].solved is True

    branches = {b["branch"] for b in engine.git_mirror.list_branches()}
    assert "progress/alice" in branches

    # Disk layout
    alice_file = engine.data_dir / "progress" / "alice" / "progress.json"
    assert alice_file.is_file()
    data = json.loads(alice_file.read_text(encoding="utf-8"))
    assert data["challenges"]["orient-find-flag"]["solved"] is True


def test_delete_challenge(tmp_path, engine):
    from academy.admin import create_challenge, default_challenge_draft, delete_challenge

    # Sandbox curriculum copy so we do not mutate the real tree
    import shutil

    sand = tmp_path / "curriculum"
    shutil.copytree(CURRICULUM, sand)
    eng = type(engine)(
        curriculum_root=sand,
        data_dir=tmp_path / "data2",
        workspace_root=tmp_path / "ws2",
    )
    draft = default_challenge_draft("orientation", "Temp Delete Me")
    draft["id"] = "orient-temp-delete-me"
    created = create_challenge(eng, draft)
    assert created["ok"] is True
    assert "orient-temp-delete-me" in eng._challenges

    removed = delete_challenge(eng, "orient-temp-delete-me")
    assert removed["ok"] is True
    assert "orient-temp-delete-me" not in eng._challenges
    assert not (Path(created["paths"]["challenge_dir"]).exists())


def test_legacy_progress_migrates_to_local(tmp_path):
    from academy.engine import AcademyEngine
    from academy.progress import ProgressRepository, ProgressStore, ChallengeProgress

    data = tmp_path / "data"
    data.mkdir()
    legacy = ProgressRepository(data / "progress.json")
    store = ProgressStore(student_id="local")
    store.challenges["orient-find-flag"] = ChallengeProgress(solved=True, completed_at=1.0)
    legacy.save(store)

    eng = AcademyEngine(
        curriculum_root=CURRICULUM,
        data_dir=data,
        workspace_root=tmp_path / "ws",
        user_id="local",
    )
    loaded = eng.progress()
    assert loaded.challenges["orient-find-flag"].solved is True
    assert (data / "progress" / "local" / "progress.json").is_file()
