#!/bin/sh
# Helper: show vault permissions (does not reveal the flag).
set -eu
echo "== vault listing =="
ls -la vault
echo
echo "== flag.txt mode =="
stat -c '%A %a %n' vault/flag.txt 2>/dev/null || stat -f '%Sp %OLp %N' vault/flag.txt
