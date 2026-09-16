#!/usr/bin/env bash
# Build ONE closed-network tarball: python3 + this folder. No pip.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
NAME="pi-sdr-academy"
OUT="${1:-$ROOT/dist/$NAME}"
rm -rf "$OUT"
mkdir -p "$OUT/vendor" "$OUT/platform" "$OUT/curriculum"

# Pure-Python PyYAML (no libyaml / no pip on the target)
if [[ -d /usr/lib/python3/dist-packages/yaml ]]; then
  cp -a /usr/lib/python3/dist-packages/yaml "$OUT/vendor/"
elif python3 -c "import yaml,os; print(os.path.dirname(yaml.__file__))" >/tmp/yaml_src.txt 2>/dev/null; then
  cp -a "$(cat /tmp/yaml_src.txt)" "$OUT/vendor/yaml"
else
  echo "Need PyYAML on the build machine to vendor." >&2
  exit 1
fi
find "$OUT/vendor" -name '*.so' -delete
find "$OUT/vendor" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp -a "$ROOT/platform/academy" "$OUT/platform/"
# Student pack: keep admin behind ACADEMY_ADMIN=1, but drop tests/cache noise
rm -rf "$OUT/platform/academy/__pycache__" "$OUT/platform/tests" 2>/dev/null || true
find "$OUT/platform" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp -a "$ROOT/curriculum/." "$OUT/curriculum/"
rm -rf "$OUT/curriculum/proposals" "$OUT/curriculum/schema" 2>/dev/null || true
find "$OUT/curriculum" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp "$ROOT/run.sh" "$OUT/run.sh"
chmod +x "$OUT/run.sh"
cp "$ROOT/LICENSE" "$OUT/LICENSE" 2>/dev/null || true

cat > "$OUT/README.txt" <<'EOF'
Pi SDR Academy
==============

Offline lab: five belts, fifty challenges, shell → IQ.
Needs: python3 only. No internet. No pip.

How to run
----------
  tar -xzf pi-sdr-academy.tar.gz
  cd pi-sdr-academy
  ./run.sh

Open the URL it prints (usually http://127.0.0.1:8080/).

How to learn
------------
  1. Press Start   → files land in ./challenge
  2. Open ./challenge, read README.txt, solve it
  3. Press Done    → grades your work

Belts unlock in order. Hints are optional. That's the whole app.

Instructor (optional)
---------------------
  ACADEMY_ADMIN=1 ./run.sh
  → http://127.0.0.1:8080/admin
EOF

mkdir -p "$ROOT/dist"
TAR="$ROOT/dist/${NAME}.tar.gz"
tar -C "$(dirname "$OUT")" -czf "$TAR" "$(basename "$OUT")"
echo "Packed $OUT"
echo "Tarball $TAR ($(du -h "$TAR" | awk '{print $1}'))"
