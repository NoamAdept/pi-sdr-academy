"""Local challenge API + dojo web UI (stdlib http.server). Offline-only."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .admin import (
    admin_enabled,
    apply_proposal,
    build_challenge_yaml,
    create_challenge,
    curriculum_overview,
    default_challenge_draft,
    list_proposals,
    module_detail,
    save_proposal,
    validate_challenge_draft,
)
from .dojos import catalog_payload, dojo_detail
from .engine import AcademyEngine
from .grading import award_flag
from .paths import resolve_flag_path, resolve_workspace
from .terminal_launch import open_workspace_terminal
from .ui_flavor import challenge_thumb_svg, display_title

STATIC_DIR = Path(__file__).resolve().parent / "static"
DOJO_HTML = STATIC_DIR / "dojo.html"
ADMIN_HTML = STATIC_DIR / "admin.html"


def _find_check(ws: Path) -> Path | None:
    for name in ("checker.py", "check.py"):
        candidate = ws / name
        if candidate.exists():
            return candidate
    check = ws / "check"
    if check.exists():
        return check
    return None


def _run_workspace_check(engine: AcademyEngine, challenge_id: str) -> dict:
    """Run the staged challenge checker; award + mark solved on success."""
    store = engine.progress()
    ws = Path(store.current_workspace or resolve_workspace())
    current = store.current_challenge_id
    marker = ws / ".challenge"
    marker_id = marker.read_text(encoding="utf-8").strip() if marker.is_file() else ""
    if current != challenge_id and marker_id != challenge_id:
        return {
            "ok": False,
            "error": "Start this challenge first (workspace does not match).",
            "workspace": str(ws),
        }
    check = _find_check(ws)
    if check is None:
        return {
            "ok": False,
            "error": "No checker in workspace. Paste a found flag instead.",
            "workspace": str(ws),
        }
    env = os.environ.copy()
    env["ACADEMY_WORKSPACE"] = str(ws)
    env["ACADEMY_DATA"] = str(engine.data_dir)
    env["ACADEMY_FLAG_PATH"] = str(resolve_flag_path())
    env["PYTHONPATH"] = str(Path(__file__).resolve().parent.parent) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    if check.suffix == ".py":
        cmd = [sys.executable, str(check)]
    elif os.access(check, os.X_OK):
        cmd = [str(check)]
    else:
        cmd = ["bash", str(check)]
    result = subprocess.run(cmd, cwd=str(ws), env=env, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stdout or result.stderr or "").strip()
        return {
            "ok": False,
            "error": "Check failed — keep working in the workspace.",
            "detail": detail[-800:] if detail else "",
            "workspace": str(ws),
        }
    flag = award_flag(ws, silent=True)
    submitted = engine.submit(challenge_id, flag)
    payload = {
        "ok": bool(submitted),
        "flag": flag if submitted else None,
        "workspace": str(ws),
        "via": "check",
    }
    if submitted:
        ch = engine.get_challenge(challenge_id)
        payload["explanation"] = ch.explanation
    return payload


def serve_api(
    curriculum_root: Path,
    data_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8080,
    *,
    admin: bool = False,
) -> None:
    engine = AcademyEngine(curriculum_root=curriculum_root, data_dir=data_dir)
    if admin:
        os.environ["ACADEMY_ADMIN"] = "1"

    class Handler(BaseHTTPRequestHandler):
        def _admin_required(self):
            if admin_enabled():
                return None
            return self._json(403, {"error": "Admin mode disabled. Run: academy admin"})

        def _read_body(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                body = {}
            return body if isinstance(body, dict) else {}
        def _json(self, code: int, payload) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _bytes(self, code: int, data: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _html_file(self, path: Path) -> None:
            if not path.is_file():
                return self._json(404, {"error": "ui missing"})
            return self._bytes(200, path.read_bytes(), "text/html; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            store = engine.progress()

            if path in ("/", "/index.html", "/dojo"):
                return self._html_file(DOJO_HTML)
            if path in ("/admin", "/admin/"):
                if not admin_enabled():
                    return self._json(403, {"error": "Admin mode disabled. Run: academy admin"})
                return self._html_file(ADMIN_HTML)
            if path.startswith("/icons/"):
                # Offline icon pack (PNG). Keep paths under static/icons only.
                name = unquote(path[len("/icons/") :].lstrip("/"))
                if "/" in name or "\\" in name or name.startswith(".") or not name.endswith(".png"):
                    return self._json(404, {"error": "not found"})
                icon = STATIC_DIR / "icons" / name
                if not icon.is_file():
                    return self._json(404, {"error": "not found"})
                return self._bytes(200, icon.read_bytes(), "image/png")
            if path.startswith("/fonts/"):
                name = unquote(path[len("/fonts/") :].lstrip("/"))
                if "/" in name or "\\" in name or name.startswith(".") or not name.endswith((".woff2", ".woff")):
                    return self._json(404, {"error": "not found"})
                font = STATIC_DIR / "fonts" / name
                if not font.is_file():
                    return self._json(404, {"error": "not found"})
                ctype = "font/woff2" if name.endswith(".woff2") else "font/woff"
                return self._bytes(200, font.read_bytes(), ctype)
            if path == "/api/admin/overview":
                denied = self._admin_required()
                if denied:
                    return denied
                return self._json(200, curriculum_overview(engine))
            if path == "/api/admin/proposals":
                denied = self._admin_required()
                if denied:
                    return denied
                return self._json(200, list_proposals(engine.curriculum_root))
            if path.startswith("/api/admin/modules/"):
                denied = self._admin_required()
                if denied:
                    return denied
                slug = unquote(path[len("/api/admin/modules/") :].strip("/"))
                detail = module_detail(engine, slug)
                if detail is None:
                    return self._json(404, {"error": "module not found"})
                return self._json(200, detail)
            if path.startswith("/api/admin/challenges/draft"):
                denied = self._admin_required()
                if denied:
                    return denied
                from urllib.parse import parse_qs

                qs = parse_qs(parsed.query or "")
                module_slug = (qs.get("module") or ["orientation"])[0]
                title = (qs.get("title") or [""])[0]
                return self._json(
                    200,
                    {"draft": default_challenge_draft(module_slug, title)},
                )
            if path == "/api/status":
                return self._json(200, engine.status_summary())
            if path == "/api/dojos":
                return self._json(200, catalog_payload(engine))
            if path.startswith("/api/dojos/"):
                dojo_id = unquote(path[len("/api/dojos/") :].strip("/"))
                detail = dojo_detail(engine, dojo_id)
                if detail is None:
                    return self._json(404, {"error": "dojo not found"})
                return self._json(200, detail)
            if path == "/api/modules":
                modules = []
                for m in engine.modules:
                    chs = []
                    for c in engine.module_challenges(m.slug):
                        prog = store.challenges.get(c.id)
                        chs.append(
                            {
                                "id": c.id,
                                "title": display_title(c.id, c.title),
                                "difficulty": c.difficulty,
                                "estimated_time": c.estimated_time,
                                "solved": bool(prog and prog.solved),
                                "thumb": f"/api/thumbs/{c.id}.svg",
                            }
                        )
                    modules.append(
                        {
                            "slug": m.slug,
                            "title": m.title,
                            "order": m.order,
                            "description": m.description,
                            "challenges": chs,
                        }
                    )
                return self._json(200, modules)
            if path.startswith("/api/thumbs/"):
                cid = unquote(path[len("/api/thumbs/") :].strip("/"))
                if cid.endswith(".svg"):
                    cid = cid[: -len(".svg")]
                if not cid:
                    return self._json(404, {"error": "not found"})
                try:
                    engine.get_challenge(cid)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                svg = challenge_thumb_svg(cid).encode("utf-8")
                return self._bytes(200, svg, "image/svg+xml; charset=utf-8")
            if path.startswith("/api/challenges/"):
                cid = path.split("/")[-1]
                try:
                    c = engine.get_challenge(cid)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                prog = store.challenges.get(cid)
                return self._json(
                    200,
                    {
                        "id": c.id,
                        "title": display_title(c.id, c.title),
                        "module": c.module,
                        "difficulty": c.difficulty,
                        "estimated_time": c.estimated_time,
                        "prerequisites": c.prerequisites,
                        "objectives": c.objectives,
                        "description": c.description,
                        "expected_tools": c.expected_tools,
                        "hints_revealed": prog.hints_revealed if prog else 0,
                        "hints_total": len(c.hints or []),
                        "solved": bool(prog and prog.solved),
                        "current": store.current_challenge_id == cid,
                        "workspace": store.current_workspace if store.current_challenge_id == cid else None,
                    },
                )
            return self._json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            body = self._read_body()

            if parsed.path == "/api/admin/challenges/validate":
                denied = self._admin_required()
                if denied:
                    return denied
                normalized = build_challenge_yaml(body)
                errors = validate_challenge_draft(normalized)
                return self._json(200, {"ok": not errors, "errors": errors, "normalized": normalized})

            if parsed.path == "/api/admin/challenges/create":
                denied = self._admin_required()
                if denied:
                    return denied
                return self._json(200, create_challenge(engine, body))

            if parsed.path == "/api/admin/proposals":
                denied = self._admin_required()
                if denied:
                    return denied
                kind = str(body.get("kind", "challenge")).strip()
                title = str(body.get("title", "Untitled")).strip() or "Untitled"
                notes = str(body.get("notes", "")).strip()
                payload = {k: v for k, v in body.items() if k not in ("kind", "title", "notes")}
                return self._json(200, save_proposal(engine.curriculum_root, kind=kind, title=title, body=payload, notes=notes))

            if parsed.path.startswith("/api/admin/proposals/") and parsed.path.endswith("/apply"):
                denied = self._admin_required()
                if denied:
                    return denied
                filename = unquote(parsed.path[len("/api/admin/proposals/") : -len("/apply")].strip("/"))
                return self._json(200, apply_proposal(engine, filename))

            if parsed.path.endswith("/hint"):
                cid = parsed.path.split("/")[-2]
                try:
                    level, text = engine.get_hint(cid)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                return self._json(200, {"level": level, "text": text})

            if parsed.path.endswith("/submit"):
                cid = parsed.path.split("/")[-2]
                flag = (body.get("flag") or "").strip()
                try:
                    engine.get_challenge(cid)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                if not flag:
                    try:
                        return self._json(200, _run_workspace_check(engine, cid))
                    except Exception as exc:  # noqa: BLE001
                        return self._json(500, {"ok": False, "error": f"Check crashed: {exc}"})
                try:
                    ok = engine.submit(cid, flag)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                payload = {"ok": ok, "via": "flag"}
                if ok:
                    ch = engine.get_challenge(cid)
                    payload["explanation"] = ch.explanation
                else:
                    payload["error"] = "Wrong flag — try again or take a hint."
                return self._json(200, payload)

            if parsed.path.endswith("/check"):
                cid = parsed.path.split("/")[-2]
                try:
                    engine.get_challenge(cid)
                except KeyError:
                    return self._json(404, {"error": "not found"})
                try:
                    return self._json(200, _run_workspace_check(engine, cid))
                except Exception as exc:  # noqa: BLE001 — keep HTTP connection alive
                    return self._json(500, {"ok": False, "error": f"Check crashed: {exc}"})

            if parsed.path.endswith("/start"):
                cid = parsed.path.split("/")[-2]
                open_term = body.get("open_terminal", True)
                if isinstance(open_term, str):
                    open_term = open_term.strip().lower() not in {"0", "false", "no", "off"}
                try:
                    dest = engine.start_challenge(cid)
                except (KeyError, RuntimeError) as exc:
                    return self._json(400, {"ok": False, "error": str(exc)})
                except Exception as exc:  # noqa: BLE001
                    return self._json(500, {"ok": False, "error": f"Start failed: {exc}"})
                payload = {
                    "ok": True,
                    "workspace": str(dest),
                    "challenge_id": cid,
                    "terminal": None,
                }
                if open_term:
                    payload["terminal"] = open_workspace_terminal(dest, challenge_id=cid)
                return self._json(200, payload)

            return self._json(404, {"error": "not found", "path": parsed.path})

        def log_message(self, fmt: str, *args) -> None:
            pass

    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.serve_forever()
