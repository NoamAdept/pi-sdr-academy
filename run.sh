#!/bin/sh
# Closed-network launcher. Needs: python3 only. No pip. No internet.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)

# Prefer this folder's code — ignore user site-packages on the host.
export PYTHONNOUSERSITE=1
export PYTHONPATH="$ROOT/vendor:$ROOT/platform"

# Docker layout puts academy/ at ROOT
if [ ! -d "$ROOT/platform/academy" ] && [ -d "$ROOT/academy" ]; then
  export PYTHONPATH="$ROOT/vendor:$ROOT"
fi

export ACADEMY_CURRICULUM="${ACADEMY_CURRICULUM:-$ROOT/curriculum}"
export ACADEMY_DATA="${ACADEMY_DATA:-$ROOT/.academy-data}"
export ACADEMY_WORKSPACE="${ACADEMY_WORKSPACE:-$ROOT/challenge}"
export ACADEMY_FLAG_PATH="${ACADEMY_FLAG_PATH:-$ROOT/.academy-data/flag.txt}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Pi SDR Academy needs python3 on PATH." >&2
  echo "No pip install required — only the python3 interpreter." >&2
  exit 1
fi

# Prove the pack is complete before opening the port.
if ! python3 -c "import yaml, academy"; then
  echo "Self-check failed: cannot import vendored yaml/academy." >&2
  echo "PYTHONPATH=$PYTHONPATH" >&2
  exit 1
fi

mkdir -p "$ACADEMY_DATA" "$ACADEMY_WORKSPACE"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"

echo ""
echo "  Pi SDR Academy  (offline / closed network)"
echo "  Open  http://$HOST:$PORT/"
echo "  Then  Start → solve in ./challenge → Done"
echo "  Admin ACADEMY_ADMIN=1 ./run.sh  →  http://$HOST:$PORT/admin"
echo "  See   MANAGE.txt for users + GitHub progress branches"
echo ""

case "${ACADEMY_ADMIN:-0}" in
  1|true|yes)
    echo "  Admin http://$HOST:$PORT/admin"
    exec python3 -m academy.cli admin --host "$HOST" --port "$PORT"
    ;;
  *)
    exec python3 -m academy.cli serve --host "$HOST" --port "$PORT"
    ;;
esac
