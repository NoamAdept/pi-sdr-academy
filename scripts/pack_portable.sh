#!/usr/bin/env bash
# Build a closed-network tarball: python3 + this folder. No pip.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
OUT="${1:-$ROOT/dist/academy-portable}"
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
cp -a "$ROOT/curriculum/." "$OUT/curriculum/"
cp "$ROOT/run.sh" "$OUT/run.sh"
chmod +x "$OUT/run.sh"

cat > "$OUT/README.txt" <<'EOF'
Pi SDR Academy — portable (closed network)
==========================================

Needs: python3 (3.11+). No internet. No pip.

  ./run.sh
  open http://127.0.0.1:8080/dojo

Admin challenge writer:
  ACADEMY_ADMIN=1 ./run.sh
  open http://127.0.0.1:8080/admin

Copy this whole folder to a USB stick / air-gapped host and run.
EOF

mkdir -p "$ROOT/dist"
TAR="$ROOT/dist/academy-portable.tgz"
tar -C "$(dirname "$OUT")" -czf "$TAR" "$(basename "$OUT")"
echo "Packed $OUT"
echo "Tarball $TAR ($(du -h "$TAR" | awk '{print $1}'))"
