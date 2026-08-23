"""Open a local terminal focused on a challenge workspace."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def open_workspace_terminal(workspace: str | Path, *, challenge_id: str = "") -> dict:
    """
    Launch a visible terminal with cwd=workspace.
    Returns {"ok": bool, "via": str|None, "error": str|None}.
    Set ACADEMY_OPEN_TERMINAL=0 to disable.
    """
    if os.environ.get("ACADEMY_OPEN_TERMINAL", "1").strip().lower() in {"0", "false", "no", "off"}:
        return {"ok": False, "via": None, "error": "disabled by ACADEMY_OPEN_TERMINAL"}

    dest = Path(workspace).expanduser().resolve()
    if not dest.is_dir():
        return {"ok": False, "via": None, "error": f"workspace missing: {dest}"}

    label = challenge_id or dest.name
    # Hard-clear scrollback + screen, then a tiny banner (no wall of text).
    clear = r"printf '\033c\033[3J'; clear 2>/dev/null; "
    banner = (
        clear
        + f"printf '\\033[1;92m%s\\033[0m  \\033[1;96m%s\\033[0m\\n' '道場' {shlex.quote(label)}; "
        + "printf '\\033[2m%s\\033[0m\\n\\n' 'ls · cat README.txt · ./check'; "
        + 'exec "$SHELL" -l'
    )
    shell_cmd = f"cd {shlex.quote(str(dest))} && {banner}"

    try:
        if sys.platform == "darwin":
            via = _open_macos(shell_cmd)
        else:
            via = _open_linux(shell_cmd, dest)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "via": None, "error": str(exc)}

    if via:
        return {"ok": True, "via": via, "error": None}
    return {"ok": False, "via": None, "error": "no terminal app found"}


def _as_quote(s: str) -> str:
    """AppleScript double-quoted string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _open_macos(shell_cmd: str) -> str | None:
    if shutil.which("osascript") is None:
        return None

    q = _as_quote(shell_cmd)

    iterm = Path("/Applications/iTerm.app")
    if iterm.exists() or _app_running("iTerm2") or _app_running("iTerm"):
        script = f"""
tell application "iTerm"
  activate
  if (count of windows) = 0 then
    create window with default profile
  else
    tell current window
      create tab with default profile
    end tell
  end if
  tell current session of current window
    write text {q}
  end tell
end tell
"""
        if _run_osascript(script):
            return "iterm"

    script = f"""
tell application "Terminal"
  activate
  do script {q}
end tell
"""
    if _run_osascript(script):
        return "terminal.app"
    return None


def _app_running(name: str) -> bool:
    try:
        r = subprocess.run(
            ["pgrep", "-x", name],
            capture_output=True,
            check=False,
        )
        return r.returncode == 0
    except OSError:
        return False


def _run_osascript(script: str) -> bool:
    r = subprocess.run(
        ["osascript"],
        input=script,
        text=True,
        capture_output=True,
        check=False,
    )
    return r.returncode == 0


def _open_linux(shell_cmd: str, dest: Path) -> str | None:
    candidates = [
        ("lxterminal", ["lxterminal", f"--working-directory={dest}", "-e", f"bash -lc {shlex.quote(shell_cmd)}"]),
        ("xfce4-terminal", ["xfce4-terminal", f"--working-directory={dest}", "-e", f"bash -lc {shlex.quote(shell_cmd)}"]),
        ("gnome-terminal", ["gnome-terminal", f"--working-directory={dest}", "--", "bash", "-lc", shell_cmd]),
        ("konsole", ["konsole", "--workdir", str(dest), "-e", "bash", "-lc", shell_cmd]),
        ("x-terminal-emulator", ["x-terminal-emulator", "-e", f"bash -lc {shlex.quote(shell_cmd)}"]),
        ("xterm", ["xterm", "-e", f"bash -lc {shlex.quote(shell_cmd)}"]),
    ]
    for name, argv in candidates:
        if not shutil.which(argv[0]):
            continue
        try:
            subprocess.Popen(  # noqa: S603
                argv,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return name
        except OSError:
            continue
    return None
