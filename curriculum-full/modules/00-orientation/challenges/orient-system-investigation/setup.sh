#!/usr/bin/env bash
# Restore the unreadable dropbox token after git checkout (git cannot store mode 000).
set -euo pipefail
DEST="${1:?workspace dest}"
if [[ -f "$DEST/echorelay/dropbox/token.txt" ]]; then
  chmod 000 "$DEST/echorelay/dropbox/token.txt"
fi
