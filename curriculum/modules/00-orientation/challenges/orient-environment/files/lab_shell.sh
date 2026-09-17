#!/bin/bash
# Launch a nested shell with lab environment configured.
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"

# Decoy — not the real flag source
export DECOY_FLAG='flag{wrong_source_use_lab_vars}'
export ACADEMY_ROLE='student'
export LAB_SESSION='orientation-env'
export LAB_HINT='Parts may be split. Order matters.'

# Session parts are planted into .lab_env at Start (not in this script).
# Source once, then delete so `cat lab_shell.sh` never reveals them.
LAB_ENV="$ROOT/.lab_env"
if [[ -f "$LAB_ENV" ]]; then
  # shellcheck disable=SC1090
  . "$LAB_ENV"
  rm -f "$LAB_ENV"
else
  echo "Lab env missing — press Start in the dojo, then run this again." >&2
  exit 1
fi

echo "Entering lab shell. Type 'exit' when done."
echo "Inspect your environment carefully."
cd "$ROOT"
exec bash --noprofile --norc
