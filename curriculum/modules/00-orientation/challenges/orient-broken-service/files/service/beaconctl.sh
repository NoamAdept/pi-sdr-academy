#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
PIDFILE="$ROOT/beacon.pid"
LOG="$ROOT/logs/beacon.log"
SECRET="$ROOT/data/.beacon_secret"
mkdir -p "$ROOT/logs"

cmd="${1:-status}"
case "$cmd" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "already running pid $(cat "$PIDFILE")"
      exit 0
    fi
    : > "$LOG"
    # Load session flag into this process, then remove the on-disk secret
    # so the live flag only exists in the running server (and /health).
    if [ -f "$SECRET" ]; then
      BEACON_SESSION_FLAG=$(cat "$SECRET")
      export BEACON_SESSION_FLAG
      rm -f "$SECRET"
    else
      # Already consumed on a prior start — keep serving without re-planting.
      # Student must Start the challenge again in the dojo for a fresh secret.
      :
    fi
    # run from challenge workspace root (parent of service/)
    cd "$ROOT/.."
    python3 "$ROOT/bin/beacon_server.py" >>"$LOG" 2>&1 &
    echo $! > "$PIDFILE"
    # Give the HTTP listener time to become ready before the student curls it.
    sleep 1
    if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "started pid $(cat "$PIDFILE")"
      echo "check: $0 logs"
    else
      echo "failed to stay up — see logs" >&2
      cat "$LOG" >&2 || true
      rm -f "$PIDFILE"
      exit 1
    fi
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      kill "$(cat "$PIDFILE")" 2>/dev/null || true
      rm -f "$PIDFILE"
      echo "stopped"
    else
      echo "not running"
    fi
    ;;
  status)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "running pid $(cat "$PIDFILE")"
    else
      echo "stopped"
    fi
    ;;
  logs)
    tail -n 50 "$LOG" 2>/dev/null || echo "(no logs yet)"
    ;;
  *)
    echo "usage: $0 {start|stop|status|logs}" >&2
    exit 1
    ;;
esac
