"""Tests for curriculum admin helpers."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CURRICULUM = ROOT / "curriculum"


@pytest.fixture()
def engine(tmp_path):
    from academy.engine import AcademyEngine

    ws = tmp_path / "workspace"
    data = tmp_path / "data"
    return AcademyEngine(curriculum_root=CURRICULUM, data_dir=data, workspace_root=ws)


@pytest.fixture()
def sandbox_curriculum(tmp_path):
    """Minimal curriculum tree for write tests."""
    mod_dir = tmp_path / "modules" / "99-test-admin"
    ch_root = mod_dir / "challenges"
    mod_dir.mkdir(parents=True)
    (mod_dir / "module.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "test-admin",
                "slug": "test-admin",
                "title": "Admin Test Module",
                "order": 99,
                "description": "Temporary module for admin tests.\n",
                "prerequisites": [],
                "challenges": [],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    ch_root.mkdir()
    return tmp_path


def test_admin_enabled_env(monkeypatch):
    from academy.admin import admin_enabled

    monkeypatch.delenv("ACADEMY_ADMIN", raising=False)
    assert admin_enabled() is False
    monkeypatch.setenv("ACADEMY_ADMIN", "1")
    assert admin_enabled() is True


def test_validate_challenge_draft_requires_hints():
    from academy.admin import default_challenge_draft, validate_challenge_draft

    draft = default_challenge_draft("orientation", "Sample")
    draft["hints"] = [{"level": 1, "text": "only one"}]
    errors = validate_challenge_draft(draft)
    assert any("two hints" in e.lower() for e in errors)


def test_build_and_validate_default_draft():
    from academy.admin import build_challenge_yaml, default_challenge_draft, validate_challenge_draft

    draft = default_challenge_draft("orientation", "Filesystem Warmup")
    normalized = build_challenge_yaml(draft)
    errors = validate_challenge_draft(normalized)
    assert errors == []
    assert normalized["id"].startswith("orientation-")


def test_create_challenge_writes_files(sandbox_curriculum):
    from academy.admin import create_challenge, default_challenge_draft
    from academy.engine import AcademyEngine

    engine = AcademyEngine(curriculum_root=sandbox_curriculum, data_dir=sandbox_curriculum / "data")
    draft = default_challenge_draft("test-admin", "Probe Challenge")
    draft["id"] = "test-admin-probe-challenge"
    draft["title"] = "Probe Challenge"

    result = create_challenge(engine, draft)
    assert result["ok"] is True

    ch_dir = sandbox_curriculum / "modules" / "99-test-admin" / "challenges" / "test-admin-probe-challenge"
    assert (ch_dir / "challenge.yaml").is_file()
    assert (ch_dir / "files" / "README.txt").is_file()

    module_data = yaml.safe_load((sandbox_curriculum / "modules" / "99-test-admin" / "module.yaml").read_text())
    assert "test-admin-probe-challenge" in module_data["challenges"]

    engine.reload()
    assert "test-admin-probe-challenge" in engine._challenges


def test_save_and_list_proposals(sandbox_curriculum):
    from academy.admin import list_proposals, save_proposal

    result = save_proposal(
        sandbox_curriculum,
        kind="curriculum_note",
        title="Move module later",
        body={"module_slug": "test-admin"},
        notes="Consider radio-path dojo",
    )
    assert result["ok"] is True
    rows = list_proposals(sandbox_curriculum)
    assert len(rows) == 1
    assert rows[0]["kind"] == "curriculum_note"


def test_curriculum_overview(engine, monkeypatch):
    from academy.admin import curriculum_overview

    monkeypatch.setenv("ACADEMY_ADMIN", "1")
    overview = curriculum_overview(engine)
    assert overview["module_count"] == 11
    assert overview["challenge_count"] == 54
    assert overview["admin_enabled"] is True
    assert overview["dojos"]
