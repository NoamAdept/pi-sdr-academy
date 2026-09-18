#!/usr/bin/env bash
# Build ONE closed-network tarball: python3 + this folder. No pip. No internet on target.
set -euo pipefail
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
NAME="pi-sdr-academy"
OUT="${1:-$ROOT/dist/$NAME}"
rm -rf "$OUT"
mkdir -p "$OUT/vendor" "$OUT/platform" "$OUT/curriculum"

# Prefer the repo's already-vendored pure-Python YAML (no .so / no libyaml).
if [[ -d "$ROOT/vendor/yaml" ]]; then
  cp -a "$ROOT/vendor/yaml" "$OUT/vendor/"
elif [[ -d /usr/lib/python3/dist-packages/yaml ]]; then
  cp -a /usr/lib/python3/dist-packages/yaml "$OUT/vendor/"
elif python3 -c "import yaml,os; print(os.path.dirname(yaml.__file__))" >/tmp/yaml_src.txt 2>/dev/null; then
  cp -a "$(cat /tmp/yaml_src.txt)" "$OUT/vendor/yaml"
else
  echo "Need vendor/yaml (or PyYAML on the build machine) to pack." >&2
  exit 1
fi

# Closed-network safety: drop native extensions and the C-libyaml wrapper.
find "$OUT/vendor" -name '*.so' -delete
find "$OUT/vendor" -name '*.pyd' -delete
rm -f "$OUT/vendor/yaml/cyaml.py"
find "$OUT/vendor" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp -a "$ROOT/platform/academy" "$OUT/platform/"
find "$OUT/platform" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find "$OUT/platform" -name '*.pyc' -delete 2>/dev/null || true

cp -a "$ROOT/curriculum/." "$OUT/curriculum/"
find "$OUT/curriculum" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

cp "$ROOT/run.sh" "$OUT/run.sh"
chmod +x "$OUT/run.sh"
cp "$ROOT/LICENSE" "$OUT/LICENSE" 2>/dev/null || true
cp "$ROOT/MANAGE.txt" "$OUT/MANAGE.txt" 2>/dev/null || true

cat > "$OUT/START_HERE.txt" <<'EOF'
CLOSED NETWORK — START HERE
===========================

Needs on the target machine: python3 (+ git if you sync progress to GitHub).
Does NOT need: pip, internet, venv, sudo, Docker.

1) tar -xzf pi-sdr-academy.tar.gz
2) cd pi-sdr-academy
3) ./run.sh
4) Open the URL it prints (usually http://127.0.0.1:8080/)

Student loop: Start → solve in ./challenge → Done

Instructor / management:
  ACADEMY_ADMIN=1 ./run.sh
  Open /admin  — users, add/remove challenges, progress sync
  Read MANAGE.txt for GitHub progress branches (progress/<user>)
EOF

cp "$OUT/START_HERE.txt" "$OUT/README.txt"

mkdir -p "$ROOT/dist"
TAR="$ROOT/dist/${NAME}.tar.gz"
tar -C "$(dirname "$OUT")" -czf "$TAR" "$(basename "$OUT")"

# Smoke-test the packed tree in isolation (no site-packages).
SMOKE=$(mktemp -d)
trap 'rm -rf "$SMOKE"' EXIT
tar -xzf "$TAR" -C "$SMOKE"
(
  cd "$SMOKE/$NAME"
  export PYTHONNOUSERSITE=1
  export PYTHONPATH="$PWD/vendor:$PWD/platform"
  python3 - <<'PY'
import sys
from pathlib import Path
# Drop host site/dist packages so we only see the pack.
sys.path = [p for p in sys.path if "site-packages" not in p and "dist-packages" not in p]
sys.path[:0] = ["vendor", "platform"]
import yaml
import academy
from academy.dojos import catalog_payload
from academy.engine import AcademyEngine
from pathlib import Path
import tempfile
assert "vendor" in yaml.__file__.replace("\\", "/")
eng = AcademyEngine(Path("curriculum"), Path(tempfile.mkdtemp()))
assert catalog_payload(eng)["next_challenge"]["id"]
print("smoke ok:", yaml.__file__)
PY
)

echo "Packed $OUT"
echo "Tarball $TAR ($(du -h "$TAR" | awk '{print $1}'))"
echo "Closed-network: copy the .tar.gz, extract, ./run.sh"
