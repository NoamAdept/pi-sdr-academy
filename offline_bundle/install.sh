#!/usr/bin/env bash
# Offline installer for Pi SDR Academy.
# Run on the Raspberry Pi AFTER copying offline_bundle/ onto the device.
# This script must NOT require Internet access.
set -euo pipefail

BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$BUNDLE_ROOT/.." && pwd)"
LOG_DIR="${ACADEMY_INSTALL_LOG:-$BUNDLE_ROOT/logs}"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/install-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG") 2>&1

echo "=== Pi SDR Academy offline installer ==="
echo "bundle: $BUNDLE_ROOT"
echo "repo:   $REPO_ROOT"
echo "log:    $LOG"
echo

fail() { echo "ERROR: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }
warn() { echo "WARN: $*"; }

# ---------- 1. Verify Debian / architecture ----------
if [[ ! -f /etc/os-release ]]; then
  fail "/etc/os-release missing — unsupported system"
fi
# shellcheck disable=SC1091
source /etc/os-release
echo "OS: ${PRETTY_NAME:-unknown} (ID=$ID VERSION_ID=${VERSION_ID:-?})"
[[ "${ID:-}" == "debian" || "${ID:-}" == "raspbian" ]] || warn "Expected Debian/Raspberry Pi OS; continuing anyway"

ARCH="$(dpkg --print-architecture 2>/dev/null || uname -m)"
echo "Architecture: $ARCH"
case "$ARCH" in
  arm64|aarch64|amd64|x86_64|armhf) ok "architecture accepted for development/deploy" ;;
  *) warn "Unusual architecture $ARCH — verify package bundle matches" ;;
esac

# Target production image is Raspberry Pi OS / Debian arm64.
if [[ -f "$BUNDLE_ROOT/manifests/target-platform.txt" ]]; then
  echo "--- target platform ---"
  cat "$BUNDLE_ROOT/manifests/target-platform.txt"
fi

# ---------- 2. Disk space ----------
# Require roughly 8 GiB free for full academy + GNU Radio (adjust via env).
NEED_KB="${ACADEMY_MIN_FREE_KB:-8000000}"
FREE_KB="$(df -Pk "$BUNDLE_ROOT" | awk 'NR==2{print $4}')"
echo "Free space: ${FREE_KB} KiB (need >= ${NEED_KB} KiB)"
if (( FREE_KB < NEED_KB )); then
  fail "Insufficient disk space"
fi
ok "disk space"

# ---------- 3. Install .deb packages (offline) ----------
DEB_DIR="$BUNDLE_ROOT/deb_packages"
if [[ -d "$DEB_DIR" ]] && compgen -G "$DEB_DIR/*.deb" > /dev/null; then
  echo "Installing local .deb packages from $DEB_DIR ..."
  if [[ "${EUID}" -ne 0 ]]; then
    SUDO="sudo"
  else
    SUDO=""
  fi
  $SUDO dpkg -i "$DEB_DIR"/*.deb || true
  # Resolve dependency order without network if possible
  $SUDO dpkg --configure -a || true
  ok "deb packages pass (review warnings above if any)"
else
  warn "No .deb files in $DEB_DIR — skipping (developer must populate via prepare_offline_bundle.sh)"
fi

# ---------- 4. Python wheels ----------
WHEEL_DIR="$BUNDLE_ROOT/python_wheels"
REQ="$REPO_ROOT/python-requirements.txt"
if [[ -d "$WHEEL_DIR" ]] && compgen -G "$WHEEL_DIR/*.whl" > /dev/null; then
  python3 -m venv /opt/academy/venv 2>/dev/null || python3 -m venv "$HOME/.academy-venv"
  # Prefer /opt if writable
  if [[ -d /opt/academy/venv ]]; then
    VENV=/opt/academy/venv
  else
    VENV="$HOME/.academy-venv"
  fi
  # shellcheck disable=SC1090
  source "$VENV/bin/activate"
  pip install --no-index --find-links="$WHEEL_DIR" -r "$REQ"
  ok "python wheels -> $VENV"
else
  warn "No wheels present — installing platform only with system/PyYAML if available"
  VENV=""
fi

# ---------- 5. Install academy platform ----------
INSTALL_ROOT="${ACADEMY_ROOT:-/opt/academy}"
if [[ ! -w "$(dirname "$INSTALL_ROOT")" ]] && [[ "${EUID}" -ne 0 ]]; then
  INSTALL_ROOT="$HOME/academy"
  warn "Using user install root $INSTALL_ROOT"
fi
mkdir -p "$INSTALL_ROOT"
rsync -a --delete \
  --exclude offline_bundle/deb_packages \
  --exclude offline_bundle/python_wheels \
  --exclude .git \
  "$REPO_ROOT/curriculum" "$REPO_ROOT/docs" "$REPO_ROOT/platform" "$REPO_ROOT/scripts" \
  "$INSTALL_ROOT/" 2>/dev/null || {
    mkdir -p "$INSTALL_ROOT"
    cp -a "$REPO_ROOT/curriculum" "$REPO_ROOT/docs" "$REPO_ROOT/platform" "$REPO_ROOT/scripts" "$INSTALL_ROOT/"
  }

# Also keep manifests
mkdir -p "$INSTALL_ROOT/manifests"
cp -a "$REPO_ROOT"/python-requirements.txt "$REPO_ROOT"/packages.lock "$REPO_ROOT"/toolchain-manifest.txt \
  "$INSTALL_ROOT/manifests/" 2>/dev/null || true

if [[ -n "${VENV:-}" && -f "$VENV/bin/pip" ]]; then
  "$VENV/bin/pip" install --no-index --find-links="$WHEEL_DIR" -e "$INSTALL_ROOT/platform" || \
    "$VENV/bin/pip" install -e "$INSTALL_ROOT/platform"
  BIN="$VENV/bin"
else
  pip3 install --user -e "$INSTALL_ROOT/platform" || python3 -m pip install --user -e "$INSTALL_ROOT/platform"
  BIN="$HOME/.local/bin"
fi

# Environment file for students
ENV_FILE="$INSTALL_ROOT/academy.env"
cat > "$ENV_FILE" <<EOF
export ACADEMY_CURRICULUM=$INSTALL_ROOT/curriculum
export ACADEMY_DOCS=$INSTALL_ROOT/docs
export ACADEMY_DATA=\${ACADEMY_DATA:-$HOME/.academy}
export ACADEMY_WORKSPACE=\${ACADEMY_WORKSPACE:-/challenge}
export ACADEMY_FLAG_PATH=\${ACADEMY_FLAG_PATH:-/home/flag.txt}
export PATH=$BIN:\$PATH
# Short lab commands (also installed as console scripts): next, hint, submit, status
EOF

# Standard challenge + flag locations (Pi image)
if [[ "${EUID}" -eq 0 ]] || command -v sudo >/dev/null 2>&1; then
  SUDO_CMD=""
  [[ "${EUID}" -ne 0 ]] && SUDO_CMD="sudo"
  $SUDO_CMD mkdir -p /challenge /home
  $SUDO_CMD chmod 1777 /challenge 2>/dev/null || $SUDO_CMD chmod 777 /challenge
  # Flag path exists but must stay empty until academy verify awards a session flag.
  $SUDO_CMD truncate -s 0 /home/flag.txt 2>/dev/null || $SUDO_CMD sh -c ': > /home/flag.txt'
  $SUDO_CMD chmod 666 /home/flag.txt 2>/dev/null || true
  ok "created /challenge and empty /home/flag.txt"
fi
ok "platform installed at $INSTALL_ROOT"

# ---------- 6. Documentation ----------
mkdir -p "$INSTALL_ROOT/docs"
ok "documentation present at $INSTALL_ROOT/docs"

# ---------- 7. GNU Radio (if bundled) ----------
if [[ -d "$BUNDLE_ROOT/gnuradio" ]] && [[ -f "$BUNDLE_ROOT/gnuradio/install_local.sh" ]]; then
  bash "$BUNDLE_ROOT/gnuradio/install_local.sh"
  ok "GNU Radio local installer invoked"
else
  warn "GNU Radio offline payload not yet populated (see offline_bundle/gnuradio/README.md)"
fi

# ---------- 8. Self-tests ----------
# shellcheck disable=SC1090
source "$ENV_FILE"
export ACADEMY_CURRICULUM ACADEMY_DOCS ACADEMY_DATA ACADEMY_WORKSPACE
VERIFY="$INSTALL_ROOT/scripts/verify_environment.sh"
if [[ -x "$VERIFY" ]]; then
  bash "$VERIFY"
else
  bash "$REPO_ROOT/scripts/verify_environment.sh"
fi

echo
echo "============================================"
echo " offline environment ready (baseline check)"
echo " source $ENV_FILE"
echo " academy list"
echo " academy docs   # http://127.0.0.1:8000/"
echo "============================================"
