"""Per-user progress stored as Git branches (auto-updated on every solve).

Layout
------
  {data}/progress/<user_id>/progress.json     live progress files
  {data}/progress-git/.git                    working git object store
  {data}/academy-progress.git                 bare repo created on first run

Each user maps to branch ``progress/<user_id>`` containing only ``progress.json``.
On first application start a bare progress repository is created and wired as
``origin``. Every progress save commits and pushes that user's branch there
automatically — no manual remote/push for the happy path.

Optionally replace ``origin`` with a GitHub (or on-prem) URL via
``ACADEMY_PROGRESS_REMOTE`` / ``academy progress remote`` / Admin → Sync.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .progress import ProgressRepository, ProgressStore

BRANCH_RE = re.compile(r"^progress/[a-z][a-z0-9_-]{1,31}$")
BARE_DIRNAME = "academy-progress.git"
AUTO_REMOTE_MARKER = "progress-remote-auto"


def progress_branch(user_id: str) -> str:
    return f"progress/{user_id}"


def _run_git(repo: Path, *args: str, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "Pi SDR Academy")
    env.setdefault("GIT_AUTHOR_EMAIL", "academy@localhost")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        input=input_text,
        env=env,
    )


class GitProgressMirror:
    """File progress + git branch mirror; auto-updates each user's branch."""

    def __init__(self, data_dir: Path, remote_url: str | None = None):
        self.data_dir = Path(data_dir)
        self.files_root = self.data_dir / "progress"
        self.git_root = self.data_dir / "progress-git"
        self.bare_root = self.data_dir / BARE_DIRNAME
        self.remote_url = (remote_url or os.environ.get("ACADEMY_PROGRESS_REMOTE") or "").strip() or None
        self.auto_remote = False
        self.files_root.mkdir(parents=True, exist_ok=True)
        self._ensure_repo()

    def _auto_remote_path(self) -> str:
        return str(self.bare_root.resolve())

    def _ensure_bare(self) -> Path:
        """Create the first-run bare progress repository if missing."""
        head = self.bare_root / "HEAD"
        if not head.exists():
            self.bare_root.mkdir(parents=True, exist_ok=True)
            # Prefer bare init into the directory itself.
            proc = subprocess.run(
                ["git", "init", "--bare", "-b", "main", str(self.bare_root)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                # Older git without -b
                subprocess.run(
                    ["git", "init", "--bare", str(self.bare_root)],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            desc = self.bare_root / "description"
            try:
                desc.write_text(
                    "Pi SDR Academy progress — one branch per operator (progress/<user>)\n",
                    encoding="utf-8",
                )
            except OSError:
                pass
        return self.bare_root

    def _ensure_repo(self) -> None:
        git_dir = self.git_root / ".git"
        created_working = False
        if not git_dir.exists():
            created_working = True
            self.git_root.mkdir(parents=True, exist_ok=True)
            _run_git(self.git_root, "init", "-b", "main", check=False)
            readme = self.git_root / "README.md"
            if not readme.exists():
                readme.write_text(
                    "# Academy progress branches\n\n"
                    "Created on first run of Pi SDR Academy.\n\n"
                    "Each `progress/<user>` branch holds that operator's `progress.json`.\n"
                    "Progress auto-commits and pushes to the local bare repo "
                    f"`{BARE_DIRNAME}` (or a configured GitHub remote).\n",
                    encoding="utf-8",
                )
                _run_git(self.git_root, "add", "README.md", check=False)
                _run_git(self.git_root, "commit", "-m", "init progress mirror", check=False)

        self._ensure_bare()

        # Resolve remote: explicit env/arg > saved config > auto bare on first run
        if self.remote_url:
            self.set_remote(self.remote_url, auto=False)
        else:
            loaded = self.load_remote_config(apply=False)
            if loaded:
                self.set_remote(loaded, auto=self._is_auto_remote(loaded))
            else:
                # First run (or no remote yet): wire origin to the bare repo.
                self.set_remote(self._auto_remote_path(), auto=True)

        if created_working:
            # Seed bare with main so the first-run repo is never empty.
            self._push_ref("main")

    def _is_auto_remote(self, url: str) -> bool:
        marker = self.data_dir / AUTO_REMOTE_MARKER
        if marker.is_file():
            return True
        try:
            return Path(url).resolve() == self.bare_root.resolve()
        except OSError:
            return False

    def set_remote(self, url: str, *, auto: bool = False) -> None:
        self.remote_url = url.strip() or None
        self.auto_remote = bool(auto and self.remote_url)
        if not self.remote_url:
            return
        remotes = _run_git(self.git_root, "remote", check=False).stdout.split()
        if "origin" in remotes:
            _run_git(self.git_root, "remote", "set-url", "origin", self.remote_url, check=False)
        else:
            _run_git(self.git_root, "remote", "add", "origin", self.remote_url, check=False)
        cfg = self.data_dir / "progress-remote.txt"
        cfg.write_text(self.remote_url + "\n", encoding="utf-8")
        marker = self.data_dir / AUTO_REMOTE_MARKER
        if self.auto_remote:
            marker.write_text("1\n", encoding="utf-8")
        elif marker.exists():
            marker.unlink()

    def load_remote_config(self, *, apply: bool = True) -> str | None:
        cfg = self.data_dir / "progress-remote.txt"
        if cfg.is_file():
            url = cfg.read_text(encoding="utf-8").strip()
            if url:
                if apply:
                    self.set_remote(url, auto=self._is_auto_remote(url))
                return url
        return self.remote_url

    def user_progress_path(self, user_id: str) -> Path:
        path = self.files_root / user_id
        path.mkdir(parents=True, exist_ok=True)
        return path / "progress.json"

    def repo_for(self, user_id: str) -> ProgressRepository:
        return ProgressRepository(self.user_progress_path(user_id))

    def migrate_legacy(self, legacy_path: Path, user_id: str = "local") -> bool:
        """Move old single-file progress.json into the per-user tree once."""
        if not legacy_path.is_file():
            return False
        dest = self.user_progress_path(user_id)
        if dest.exists() and dest.stat().st_size > 2:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_path, dest)
        self.commit_user(user_id, message="migrate legacy progress.json")
        return True

    def _blob_oid(self, content: bytes) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.git_root), "hash-object", "-w", "--stdin"],
            input=content,
            capture_output=True,
            check=True,
        )
        return proc.stdout.decode().strip()

    def _mktree(self, blob_oid: str) -> str:
        listing = f"100644 blob {blob_oid}\tprogress.json\n"
        proc = _run_git(self.git_root, "mktree", input_text=listing)
        return proc.stdout.strip()

    def _commit_tree(self, tree: str, message: str, parent: str | None) -> str:
        args = ["commit-tree", tree]
        if parent:
            args.extend(["-p", parent])
        proc = _run_git(self.git_root, *args, input_text=message + "\n")
        return proc.stdout.strip()

    def _push_ref(self, ref: str) -> dict:
        """Push one local ref to origin (branch name or refs/heads/...)."""
        self.load_remote_config()
        if not self.remote_url:
            return {"ok": False, "error": "no remote"}
        if ref.startswith("refs/"):
            src = ref
            dst = ref
        else:
            src = f"refs/heads/{ref}"
            dst = f"refs/heads/{ref}"
        proc = _run_git(
            self.git_root,
            "push",
            "-u",
            "origin",
            f"{src}:{dst}",
            check=False,
        )
        combined = (proc.stdout or "") + (proc.stderr or "")
        ok = proc.returncode == 0 or "Everything up-to-date" in combined
        return {
            "ok": ok,
            "remote": self.remote_url,
            "ref": ref,
            "stdout": (proc.stdout or "")[-400:],
            "stderr": (proc.stderr or "")[-400:],
        }

    def push_user(self, user_id: str) -> dict:
        """Push a single operator's progress/<user> branch to origin."""
        branch = progress_branch(user_id)
        if not BRANCH_RE.fullmatch(branch):
            return {"ok": False, "error": f"invalid branch {branch}"}
        tip = _run_git(
            self.git_root, "rev-parse", "-q", "--verify", f"refs/heads/{branch}", check=False
        )
        if tip.returncode != 0 or not tip.stdout.strip():
            return {"ok": False, "error": f"no local branch {branch}"}
        return self._push_ref(branch)

    def commit_user(self, user_id: str, message: str | None = None, *, auto_push: bool = True) -> dict:
        path = self.user_progress_path(user_id)
        if not path.is_file():
            ProgressRepository(path).save(ProgressStore(student_id=user_id))
        content = path.read_bytes()
        branch = progress_branch(user_id)
        if not BRANCH_RE.fullmatch(branch):
            return {"ok": False, "error": f"invalid branch {branch}"}

        tip = _run_git(
            self.git_root, "rev-parse", "-q", "--verify", f"refs/heads/{branch}", check=False
        )
        parent = tip.stdout.strip() or None

        # Skip empty commit if content unchanged
        if parent:
            show = _run_git(
                self.git_root, "show", f"{parent}:progress.json", check=False
            )
            if show.returncode == 0 and show.stdout.encode() == content:
                result = {"ok": True, "branch": branch, "commit": parent, "unchanged": True}
                if auto_push:
                    try:
                        result["push"] = self.push_user(user_id)
                    except Exception as exc:  # noqa: BLE001
                        result["push"] = {"ok": False, "error": str(exc)}
                return result

        blob = self._blob_oid(content)
        tree = self._mktree(blob)
        msg = message or f"progress for {user_id} @ {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
        commit = self._commit_tree(tree, msg, parent)
        _run_git(self.git_root, "update-ref", f"refs/heads/{branch}", commit)
        result = {"ok": True, "branch": branch, "commit": commit, "unchanged": False}
        if auto_push:
            try:
                result["push"] = self.push_user(user_id)
            except Exception as exc:  # noqa: BLE001 — never fail a solve on push
                result["push"] = {"ok": False, "error": str(exc)}
        return result

    def commit_all_users(self) -> list[dict]:
        results = []
        for path in sorted(self.files_root.iterdir()) if self.files_root.is_dir() else []:
            if path.is_dir() and (path / "progress.json").is_file():
                results.append(self.commit_user(path.name))
        return results

    def list_branches(self) -> list[dict]:
        proc = _run_git(
            self.git_root,
            "for-each-ref",
            "--format=%(refname:short)|%(objectname:short)|%(committerdate:iso-strict)",
            "refs/heads/progress",
            check=False,
        )
        rows = []
        for line in proc.stdout.splitlines():
            if not line.strip() or "|" not in line:
                continue
            name, oid, when = line.split("|", 2)
            rows.append({"branch": name, "commit": oid, "when": when, "user_id": name.split("/", 1)[-1]})
        return rows

    def list_remote_branches(self) -> list[dict]:
        """List progress/* branches present on the bare/remote repo."""
        if not self.remote_url:
            return []
        # For local bare repos, inspect refs directly (works offline).
        bare = Path(self.remote_url)
        if bare.is_dir() and (bare / "HEAD").exists():
            proc = _run_git(
                bare,
                "for-each-ref",
                "--format=%(refname:short)|%(objectname:short)|%(committerdate:iso-strict)",
                "refs/heads/progress",
                check=False,
            )
            rows = []
            for line in proc.stdout.splitlines():
                if not line.strip() or "|" not in line:
                    continue
                name, oid, when = line.split("|", 2)
                rows.append(
                    {
                        "branch": name,
                        "commit": oid,
                        "when": when,
                        "user_id": name.split("/", 1)[-1],
                    }
                )
            return rows
        return []

    def materialize_branch(self, user_id: str) -> bool:
        """Write progress.json on disk from the git branch tip (after pull)."""
        branch = progress_branch(user_id)
        show = _run_git(self.git_root, "show", f"{branch}:progress.json", check=False)
        if show.returncode != 0:
            return False
        path = self.user_progress_path(user_id)
        path.write_text(show.stdout, encoding="utf-8")
        return True

    def push_all(self) -> dict:
        self.load_remote_config()
        if not self.remote_url:
            return {
                "ok": False,
                "error": "No remote configured. Set ACADEMY_PROGRESS_REMOTE or admin → Sync.",
            }
        self.commit_all_users()
        proc = _run_git(
            self.git_root,
            "push",
            "-u",
            "origin",
            "refs/heads/progress/*:refs/heads/progress/*",
            check=False,
        )
        main = _run_git(self.git_root, "push", "-u", "origin", "main", check=False)
        ok = proc.returncode == 0 or "Everything up-to-date" in (proc.stderr + proc.stdout)
        return {
            "ok": ok,
            "remote": self.remote_url,
            "auto_remote": self.auto_remote,
            "stdout": (proc.stdout or "")[-800:],
            "stderr": (proc.stderr or "")[-800:],
            "main_stderr": (main.stderr or "")[-400:],
            "branches": self.list_branches(),
            "remote_branches": self.list_remote_branches(),
        }

    def pull_all(self) -> dict:
        self.load_remote_config()
        if not self.remote_url:
            return {
                "ok": False,
                "error": "No remote configured. Set ACADEMY_PROGRESS_REMOTE or admin → Sync.",
            }
        proc = _run_git(
            self.git_root,
            "fetch",
            "origin",
            "refs/heads/progress/*:refs/heads/progress/*",
            check=False,
        )
        restored = []
        for row in self.list_branches():
            if self.materialize_branch(row["user_id"]):
                restored.append(row["user_id"])
        ok = proc.returncode == 0 or "progress" in (proc.stdout + proc.stderr).lower() or not proc.stderr
        if proc.returncode != 0 and "Couldn't find remote ref" in proc.stderr:
            ok = True
        return {
            "ok": ok or bool(restored),
            "remote": self.remote_url,
            "auto_remote": self.auto_remote,
            "stdout": (proc.stdout or "")[-800:],
            "stderr": (proc.stderr or "")[-800:],
            "restored_users": restored,
            "branches": self.list_branches(),
        }

    def status(self) -> dict:
        self.load_remote_config()
        return {
            "remote": self.remote_url,
            "auto_remote": self.auto_remote,
            "bare_repo": str(self.bare_root),
            "bare_exists": (self.bare_root / "HEAD").exists(),
            "git_dir": str(self.git_root),
            "files_dir": str(self.files_root),
            "branches": self.list_branches(),
            "remote_branches": self.list_remote_branches(),
            "users_on_disk": sorted(
                p.name for p in self.files_root.iterdir() if p.is_dir()
            )
            if self.files_root.is_dir()
            else [],
        }
