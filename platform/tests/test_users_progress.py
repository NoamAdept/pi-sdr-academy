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

    # First-run bare progress repository is created and wired as origin
    bare = engine.data_dir / "academy-progress.git"
    assert (bare / "HEAD").is_file()
    st = engine.git_mirror.status()
    assert st["auto_remote"] is True
    assert st["bare_exists"] is True
    assert "academy-progress.git" in (st["remote"] or "")

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

    # Auto-push landed the branch on the first-run bare repo
    remote_branches = {b["branch"] for b in engine.git_mirror.list_remote_branches()}
    assert "progress/alice" in remote_branches

    # Disk layout
    alice_file = engine.data_dir / "progress" / "alice" / "progress.json"
    assert alice_file.is_file()
    data = json.loads(alice_file.read_text(encoding="utf-8"))
    assert data["challenges"]["orient-find-flag"]["solved"] is True

    # Login rejects unknown usernames
    try:
        engine.set_user("not-a-real-user")
        raise AssertionError("expected unknown username to fail")
    except RuntimeError as exc:
        assert "Unknown username" in str(exc)


def test_first_run_creates_progress_repo(tmp_path):
    from academy.engine import AcademyEngine

    data = tmp_path / "fresh-data"
    eng = AcademyEngine(
        curriculum_root=CURRICULUM,
        data_dir=data,
        workspace_root=tmp_path / "ws-fresh",
    )
    bare = data / "academy-progress.git"
    assert bare.is_dir()
    assert (bare / "HEAD").is_file()
    assert (data / "progress-git" / ".git").exists()
    assert (data / "progress-remote.txt").is_file()
    remote = (data / "progress-remote.txt").read_text(encoding="utf-8").strip()
    assert remote.endswith("academy-progress.git")
    # main seeded on bare
    import subprocess

    refs = subprocess.run(
        ["git", "-C", str(bare), "show-ref"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "refs/heads/main" in refs.stdout


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
