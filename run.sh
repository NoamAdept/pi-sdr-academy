#!/bin/sh
# Closed-network launcher. Needs: python3 only (PyYAML is vendored).
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
export PYTHONPATH="$ROOT/vendor:$ROOT/platform${PYTHONPATH:+:$PYTHONPATH}"
# Docker layout puts academy/ at ROOT
if [ ! -d "$ROOT/platform/academy" ] && [ -d "$ROOT/academy" ]; then
  export PYTHONPATH="$ROOT/vendor:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
fi
export ACADEMY_CURRICULUM="${ACADEMY_CURRICULUM:-$ROOT/curriculum}"
export ACADEMY_DATA="${ACADEMY_DATA:-$ROOT/.academy-data}"
export ACADEMY_WORKSPACE="${ACADEMY_WORKSPACE:-$ROOT/challenge}"
export ACADEMY_FLAG_PATH="${ACADEMY_FLAG_PATH:-$ROOT/.academy-data/flag.txt}"
mkdir -p "$ACADEMY_DATA" "$ACADEMY_WORKSPACE"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
echo "Pi SDR Academy  http://$HOST:$PORT/dojo"
case "${ACADEMY_ADMIN:-0}" in
  1|true|yes)
    echo "Admin           http://$HOST:$PORT/admin"
    exec python3 -m academy.cli admin --host "$HOST" --port "$PORT"
    ;;
  *)
    exec python3 -m academy.cli serve --host "$HOST" --port "$PORT"
    ;;
esac
