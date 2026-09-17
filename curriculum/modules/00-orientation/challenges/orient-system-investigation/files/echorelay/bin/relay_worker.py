#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import sys
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
    workspace = root.parent
    conf = load_conf(root / "config" / "relay.conf")
    host = conf["listen_host"]
    port = int(conf["listen_port"])
    dropbox = Path(conf["dropbox_path"])
    if not dropbox.is_absolute():
        dropbox = (workspace / dropbox).resolve()
    log_path = Path(conf["log_path"])
    if not log_path.is_absolute():
        log_path = (workspace / log_path).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(msg + "\n")

    try:
        token = dropbox.read_text(encoding="utf-8").strip()
    except OSError as exc:
        log(f"ERROR: cannot read dropbox {dropbox}: {exc}")
        print(exc, file=sys.stderr)
        return 2

    if token != "TOKEN-ORIENT-7741":
        log(f"ERROR: unexpected token")
        return 3

    # Live flag comes from the process environment (set by relayctl at start).
    # It is never stored in this script on disk.
    flag = os.environ.get("RELAY_SESSION_FLAG", "").strip()
    if not flag:
        log("ERROR: RELAY_SESSION_FLAG missing — restart via relayctl after Start")
        print("missing RELAY_SESSION_FLAG", file=sys.stderr)
        return 4

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(5)
    log(f"INFO: listening on {host}:{port}")
    print(f"relay on {host}:{port}", flush=True)
    while True:
        conn, _addr = srv.accept()
        with conn:
            data = conn.recv(64).decode("utf-8", errors="replace").strip()
            if data == "PING":
                conn.sendall(f"PONG {flag}\n".encode("utf-8"))
            else:
                conn.sendall(b"ERR\n")


if __name__ == "__main__":
    raise SystemExit(main())
