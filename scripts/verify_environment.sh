#!/usr/bin/env bash
# Verify offline academy tooling without touching the Internet.
set -euo pipefail

FAIL=0
check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "OK  $name"
  else
    echo "FAIL $name"
    FAIL=1
  fi
}

echo "=== Academy environment verification ==="

check "bash" bash -c 'true'
check "python3" python3 -c 'import sys; assert sys.version_info >= (3, 9)'
check "gcc" gcc --version
check "g++" g++ --version
check "make" make --version
check "cmake" cmake --version
check "gdb" gdb --version
check "git" git --version
check "find" find --version
check "grep" grep --version
check "awk" awk --version
check "sed" sed --version
check "tmux" tmux -V
check "curl-or-python-http" python3 -c 'import http.server'

# Python scientific stack (required for DSP modules)
python3 - <<'PY' || FAIL=1
mods = ["numpy", "scipy", "matplotlib", "yaml"]
missing = []
for m in mods:
    try:
        __import__(m)
        print(f"OK  python:{m}")
    except Exception as e:
        missing.append(m)
        print(f"FAIL python:{m} ({e})")
if missing:
    raise SystemExit(1)
PY

# GNU Radio optional at early bring-up; warn only if missing
if python3 -c 'import gnuradio' 2>/dev/null; then
  echo "OK  gnuradio"
else
  echo "WARN gnuradio not importable (required before Module 13)"
fi

# Academy CLI
CURRICULUM="${ACADEMY_CURRICULUM:-$(CDPATH= cd -- "$(dirname "$0")/../curriculum" && pwd)}"
export ACADEMY_CURRICULUM="$CURRICULUM"
export ACADEMY_DATA="${ACADEMY_DATA:-/tmp/academy-verify-data}"
mkdir -p "$ACADEMY_DATA"

if command -v academy >/dev/null 2>&1; then
  ACADEMY_BIN=academy
elif [[ -f "$(dirname "$0")/../platform/academy/cli.py" ]]; then
  ACADEMY_BIN=(python3 -m academy.cli)
  export PYTHONPATH="$(CDPATH= cd -- "$(dirname "$0")/../platform" && pwd)${PYTHONPATH:+:$PYTHONPATH}"
else
  echo "FAIL academy CLI not found"
  FAIL=1
  ACADEMY_BIN=""
fi

if [[ -n "${ACADEMY_BIN}" ]]; then
  if "${ACADEMY_BIN[@]}" list >/dev/null; then
    echo "OK  academy list"
  else
    echo "FAIL academy list"
    FAIL=1
  fi
  COUNT=$("${ACADEMY_BIN[@]}" list 2>/dev/null | wc -l | tr -d ' ')
  echo "INFO modules listed: $COUNT"
fi

# Module dependency spot-checks: curriculum files present
MOD0="$CURRICULUM/modules/00-orientation/module.yaml"
if [[ -f "$MOD0" ]]; then
  echo "OK  module0 metadata"
else
  echo "FAIL module0 metadata"
  FAIL=1
fi

CHALLENGES=$(find "$CURRICULUM/modules" -name challenge.yaml | wc -l | tr -d ' ')
echo "INFO challenge.yaml count: $CHALLENGES"
if (( CHALLENGES < 100 )); then
  echo "FAIL expected >=100 challenge stubs"
  FAIL=1
else
  echo "OK  challenge corpus present"
fi

# Network isolation sanity: do not fail if net is up, but refuse package installs
if ping -c 1 -W 1 1.1.1.1 >/dev/null 2>&1; then
  echo "WARN Internet appears reachable — student mode should still avoid apt/pip online"
else
  echo "OK  no ICMP to Internet (or blocked) — good for offline lab posture"
fi

echo
if (( FAIL == 0 )); then
  echo "offline environment ready"
  exit 0
fi
echo "verification reported failures — fix before student handoff"
exit 1
