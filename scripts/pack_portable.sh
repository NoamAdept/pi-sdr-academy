#!/usr/bin/env bash
# Build ONE closed-network tarball: python3 + this folder. No pip.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
NAME="pi-sdr-academy"
OUT="${1:-$ROOT/dist/$NAME}"
rm -rf "$OUT"
mkdir -p "$OUT/vendor" "$OUT/platform" "$OUT/curriculum"

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
find "$OUT/platform" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp -a "$ROOT/curriculum/." "$OUT/curriculum/"
find "$OUT/curriculum" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp "$ROOT/run.sh" "$OUT/run.sh"
chmod +x "$OUT/run.sh"
cp "$ROOT/LICENSE" "$OUT/LICENSE" 2>/dev/null || true

cat > "$OUT/README.txt" <<'EOF'
Pi SDR Academy
==============

Needs: python3. No internet. No pip.

  ./run.sh
  open the URL it prints

Then: Start → solve in ./challenge → Done
EOF

mkdir -p "$ROOT/dist"
TAR="$ROOT/dist/${NAME}.tar.gz"
tar -C "$(dirname "$OUT")" -czf "$TAR" "$(basename "$OUT")"
echo "Packed $OUT"
echo "Tarball $TAR ($(du -h "$TAR" | awk '{print $1}'))"
