#!/bin/bash
# Launch a nested shell with lab environment configured.
set -euo pipefail
ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"

# Decoy — not the real flag source
export DECOY_FLAG='flag{wrong_source_use_lab_vars}'
export ACADEMY_ROLE='student'
export LAB_SESSION='orientation-env'
export LAB_FLAG_PART1='flag{env_vars_are_'
export LAB_FLAG_PART2='process_state}'
export LAB_HINT='Parts may be split. Order matters.'

echo "Entering lab shell. Type 'exit' when done."
echo "Inspect your environment carefully."
cd "$ROOT"
exec bash --noprofile --norc
