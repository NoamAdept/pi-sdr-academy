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
    assert len(modules) == 11
    assert modules[0].slug == "orientation"


def test_env_challenge_flag_not_in_lab_shell(engine, tmp_path):
    """Live session flag must not be readable via `cat lab_shell.sh`."""
    from academy.progress import ChallengeProgress

    store = engine.progress()
    store.challenges["orient-process-hunt"] = ChallengeProgress(solved=True)
    engine.progress_repo.save(store)

    dest = engine.start_challenge("orient-environment")
    script = (dest / "lab_shell.sh").read_text(encoding="utf-8")
    lab_env = dest / ".lab_env"
    assert lab_env.is_file()
    parts = lab_env.read_text(encoding="utf-8")
    assert "LAB_FLAG_PART1" in parts and "LAB_FLAG_PART2" in parts
    # Script may mention the decoy only — never the live session exports.
    assert "export LAB_FLAG_PART1='flag" not in script
    assert "export LAB_FLAG_PART2='flag" not in script
    live = "".join(
        line.split("=", 1)[1].strip().strip("'\"")
        for line in parts.splitlines()
        if line.startswith("export LAB_FLAG_PART")
    )
    assert live.startswith("flag{")
    assert live not in script


def test_silent_port_flag_not_in_json(engine):
    """Silent Port flag must not sit in beacon_ok.json for a casual cat."""
    import json
    import os
    import subprocess
    from academy.progress import ChallengeProgress

    store = engine.progress()
    for cid in ("orient-process-hunt", "orient-environment"):
        store.challenges[cid] = ChallengeProgress(solved=True)
    engine.progress_repo.save(store)

    dest = engine.start_challenge("orient-broken-service")
    ok_json = dest / "service" / "data" / "beacon_ok.json"
    secret = dest / "service" / "data" / ".beacon_secret"
    assert secret.is_file()
    live = secret.read_text(encoding="utf-8").strip()
    assert live.startswith("flag{")
    data = json.loads(ok_json.read_text(encoding="utf-8"))
    assert "flag" not in data or not str(data.get("flag", "")).startswith("flag{local")
    assert live not in ok_json.read_text(encoding="utf-8")

    # Fix config so the service can start, then prove /health gets the flag
    # only after beaconctl consumes the secret.
    conf = dest / "service" / "config" / "beacon.conf"
    conf.write_text(
        "listen_host=127.0.0.1\n"
        "listen_port=18765\n"
        "data_path=service/data/beacon_ok.json\n"
        "log_path=service/logs/beacon.log\n",
        encoding="utf-8",
    )
    ctl = dest / "service" / "beaconctl.sh"
    os.chmod(ctl, 0o755)
    start = subprocess.run(
        ["bash", str(ctl), "start"],
        cwd=str(dest),
        capture_output=True,
        text=True,
        check=False,
    )
    assert start.returncode == 0, start.stdout + start.stderr
    assert not secret.exists()  # consumed at start
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:18765/health", timeout=3) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        assert body.get("flag") == live
    finally:
        subprocess.run(["bash", str(ctl), "stop"], cwd=str(dest), check=False)


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
    assert n == 54


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


def test_system_investigation_flag_not_in_scripts(engine):
    """System Investigation live flag must not sit in cat-able scripts."""
    import socket
    import subprocess
    import time
    from academy.progress import ChallengeProgress
    from academy.secrets import load_session_flag

    store = engine.progress()
    for cid in (
        "orient-find-flag",
        "orient-permissions",
        "orient-process-hunt",
        "orient-environment",
        "orient-broken-service",
    ):
        store.challenges[cid] = ChallengeProgress(solved=True)
    engine.progress_repo.save(store)

    dest = engine.start_challenge("orient-system-investigation")
    live = load_session_flag(engine.data_dir, "orient-system-investigation")
    assert live and live.startswith("flag{")

    worker = dest / "echorelay" / "bin" / "relay_worker.py"
    verify = dest / "echorelay" / "verify.sh"
    ctl = dest / "echorelay" / "relayctl.sh"
    secret = dest / "echorelay" / "data" / ".relay_secret"
    assert secret.is_file()
    assert secret.read_text(encoding="utf-8").strip() == live
    assert live not in worker.read_text(encoding="utf-8")
    assert live not in verify.read_text(encoding="utf-8")
    assert live not in ctl.read_text(encoding="utf-8")

    # Align config + dropbox mode so the worker can serve, then prove PING.
    conf = dest / "echorelay" / "config" / "relay.conf"
    conf.write_text(
        "listen_host=127.0.0.1\n"
        "listen_port=9471\n"
        "dropbox_path=echorelay/dropbox/token.txt\n"
        "log_path=echorelay/logs/relay.log\n",
        encoding="utf-8",
    )
    token = dest / "echorelay" / "dropbox" / "token.txt"
    os.chmod(token, 0o644)
    os.chmod(ctl, 0o755)
    start = subprocess.run(
        ["bash", str(ctl), "start"],
        cwd=str(dest),
        capture_output=True,
        text=True,
        check=False,
    )
    assert start.returncode == 0, start.stdout + start.stderr
    assert not secret.exists()
    try:
        time.sleep(0.2)
        with socket.create_connection(("127.0.0.1", 9471), timeout=2) as sock:
            sock.sendall(b"PING\n")
            resp = sock.recv(256).decode("utf-8", errors="replace")
        assert live in resp
    finally:
        subprocess.run(["bash", str(ctl), "stop"], cwd=str(dest), check=False)


def test_plant_refuses_script_targets(engine, tmp_path):
    """Engine must refuse planting a live flag into a .py/.sh path."""
    from academy.engine import _plant_session_flag

    script = tmp_path / "evil.py"
    script.write_text('flag = "flag{template_value_here}"\n', encoding="utf-8")
    try:
        _plant_session_flag(script, "flag{session_should_not_land}")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "Refusing" in str(exc)
    assert "flag{session_should_not_land}" not in script.read_text(encoding="utf-8")


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


def test_profile_payload_calendar_and_mountain(engine):
    import time
    from academy.dojos import profile_payload
    from academy.progress import ChallengeProgress

    store = engine.progress()
    now = time.time()
    store.challenges["orient-find-flag"] = ChallengeProgress(
        started_at=now - 100,
        completed_at=now - 50,
        solved=True,
    )
    store.challenges["orient-permissions"] = ChallengeProgress(
        started_at=now - 40,
        completed_at=now - 20,
        solved=True,
    )
    engine.progress_repo.save(store)

    profile = profile_payload(engine)
    assert profile["solved"] == 2
    assert profile["total"] == 54
    # Two white-belt solves out of 10, across 5 equal terraces → 4%
    assert profile["ascent_pct"] == 4.0
    assert len(profile["belts"]) == 5
    assert profile["belts"][0]["belt"] == "white"
    assert profile["belts"][0]["solved"] == 2
    assert profile["days"]
    assert sum(profile["days"].values()) == 2
    assert profile["recent"][0]["id"] in {"orient-find-flag", "orient-permissions"}
    assert profile["streak"] >= 1

    # Progress on a later belt still counts toward ascent even if earlier belts incomplete
    store.challenges["py-control-flow"] = ChallengeProgress(
        started_at=now - 10,
        completed_at=now - 5,
        solved=True,
    )
    engine.progress_repo.save(store)
    profile2 = profile_payload(engine)
    assert profile2["solved"] == 3
    assert profile2["ascent_pct"] == 6.0  # 2/10 white + 1/10 yellow → 3/50 of mountain