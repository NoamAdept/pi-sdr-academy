#!/usr/bin/env python3
"""Minimal localhost beacon for orientation hard challenge."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def load_conf(path: Path) -> dict:
    conf = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        conf[k.strip()] = v.strip()
    return conf


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    conf_path = root / "config" / "beacon.conf"
    conf = load_conf(conf_path)
    host = conf.get("listen_host", "127.0.0.1")
    port = int(conf.get("listen_port", "8765"))
    data_path = Path(conf.get("data_path", "service/data/beacon_ok.json"))
    if not data_path.is_absolute():
        # resolve relative to challenge workspace (parent of service/)
        data_path = (root.parent / data_path).resolve()
    log_path = Path(conf.get("log_path", "service/logs/beacon.log"))
    if not log_path.is_absolute():
        log_path = (root.parent / log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(msg + "\n")

    if host not in ("127.0.0.1", "localhost", "::1"):
        log(f"ERROR: refuse to bind non-loopback host={host}")
        print(f"refusing non-loopback bind: {host}", file=sys.stderr)
        return 2
    if not data_path.is_file():
        log(f"ERROR: data file missing: {data_path}")
        print(f"missing data file: {data_path}", file=sys.stderr)
        return 3

    payload = json.loads(data_path.read_text(encoding="utf-8"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path.rstrip("/") == "/health":
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, fmt, *args):
            log("%s - %s" % (self.address_string(), fmt % args))

    httpd = ThreadingHTTPServer((host, port), Handler)
    log(f"INFO: listening on {host}:{port}")
    print(f"beacon listening on http://{host}:{port}/health", flush=True)
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
