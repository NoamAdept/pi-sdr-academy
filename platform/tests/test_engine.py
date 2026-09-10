"""Smoke tests for academy engine (offline)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CURRICULUM = ROOT / "curriculum"


@pytest.fixture()
def engine(tmp_path):
    from academy.engine import AcademyEngine

    ws = tmp_path / "workspace"
    data = tmp_path / "data"
    return AcademyEngine(curriculum_root=CURRICULUM, data_dir=data, workspace_root=ws)


def test_modules_loaded(engine):
    modules = engine.modules
    assert len(modules) == 10
    assert modules[0].slug == "orientation"


def test_orientation_challenges(engine):
    chs = engine.module_challenges("orientation")
    ids = {c.id for c in chs}
    assert "orient-find-flag" in ids
    assert len(chs) == 6


def test_start_and_submit_find_flag(engine):
    dest = engine.start_challenge("orient-find-flag")
    assert dest == engine.workspace_root
    assert (dest / "NOTES.txt").exists()
    assert (dest / "labyrinth").exists()
    assert not (dest / "BRIEFING.md").exists()
    assert not (dest / "README.md").exists()
    assert not (dest / "submit").exists()
    assert (dest / ".challenge").read_text().strip() == "orient-find-flag"
    flag_file = dest / "labyrinth/east/tunnel/.cache/secret.flag"
    assert flag_file.exists()
    flag = flag_file.read_text(encoding="utf-8").strip()
    assert engine.submit("orient-find-flag", flag) is True
    assert engine.submit("orient-find-flag", "flag{nope}") is False


def test_next_available_and_current(engine):
    nxt = engine.next_available_challenge()
    assert nxt is not None
    assert nxt.id == "orient-find-flag"
    dest = engine.start_challenge(nxt.id)
    assert dest == engine.workspace_root
    assert engine.current_challenge().id == "orient-find-flag"
    assert engine.progress().current_workspace == str(dest)
    flag = (dest / "labyrinth/east/tunnel/.cache/secret.flag").read_text().strip()
    assert engine.submit("orient-find-flag", flag)
    nxt2 = engine.next_available_challenge()
    assert nxt2 is not None
    assert nxt2.id == "orient-permissions"
    dest2 = engine.start_challenge(nxt2.id)
    assert dest2 == dest  # same directory every time
    assert (dest2 / ".challenge").read_text().strip() == "orient-permissions"
    assert not (dest2 / "labyrinth").exists()  # previous challenge cleared


def test_hints_progressive(engine):
    level1, text1 = engine.get_hint("orient-find-flag")
    assert level1 == 1
    assert text1
    level2, text2 = engine.get_hint("orient-find-flag")
    assert level2 == 2
    assert text2 != text1


def test_challenge_yaml_count():
    n = len(list(CURRICULUM.glob("modules/*/challenges/*/challenge.yaml")))
    assert n == 50


def test_session_flag_randomized_and_flag_file_cleared(engine, tmp_path):
    # Point flag path into tmp via env so we do not touch ~/flag.txt
    import os
    from academy.paths import resolve_flag_path
    flag_path = tmp_path / "flag.txt"
    flag_path.write_text("stale\n", encoding="utf-8")
    os.environ["ACADEMY_FLAG_PATH"] = str(flag_path)
    # recreate engine with same dirs but new env
    from academy.engine import AcademyEngine
    eng = AcademyEngine(
        curriculum_root=engine.curriculum_root,
        data_dir=engine.data_dir,
        workspace_root=engine.workspace_root,
    )
    eng.flag_path = flag_path
    dest = eng.start_challenge("orient-find-flag")
    assert not flag_path.exists() or flag_path.read_text().strip() == ""
    planted = (dest / "labyrinth/east/tunnel/.cache/secret.flag").read_text().strip()
    assert planted.startswith("flag{")
    assert planted != "flag{pwd_ls_find_cat_navigator}"
    # nonce is 6 hex
    import re
    assert re.fullmatch(r"flag\{pwd_ls_find_cat_navigator_[0-9a-f]{6}\}", planted)
    assert eng.submit("orient-find-flag", planted)
    # curriculum template alone must not work once session minted
    assert not eng.submit("orient-find-flag", "flag{pwd_ls_find_cat_navigator}")


def test_verify_awards_session_flag(engine, tmp_path, monkeypatch):
    import os
    from academy.grading import award_flag, expected_answer
    from academy.secrets import load_session_flag

    flag_path = tmp_path / "home_flag.txt"
    os.environ["ACADEMY_FLAG_PATH"] = str(flag_path)
    os.environ["ACADEMY_DATA"] = str(engine.data_dir)
    eng = engine
    eng.flag_path = flag_path
    dest = eng.start_challenge("orient-find-flag")
    os.environ["ACADEMY_WORKSPACE"] = str(dest)
    # answer (template) used by decode-style checkers
    assert expected_answer(dest) == "flag{pwd_ls_find_cat_navigator}"
    session = load_session_flag(engine.data_dir, "orient-find-flag")
    assert session and session != expected_answer(dest)
    awarded = award_flag(dest, silent=True)
    assert awarded == session
    assert flag_path.read_text().strip() == session
