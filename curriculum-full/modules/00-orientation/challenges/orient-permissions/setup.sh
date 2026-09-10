#!/usr/bin/env bash
# Restore the locked-down vault file after git checkout (git cannot store mode 000).
set -euo pipefail
DEST="${1:?workspace dest}"
if [[ -f "$DEST/vault/flag.txt" ]]; then
  chmod 000 "$DEST/vault/flag.txt"
fi
