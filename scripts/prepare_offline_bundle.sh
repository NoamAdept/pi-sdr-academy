#!/usr/bin/env bash
# Developer-side helper: download pinned packages WHILE ONLINE into offline_bundle/.
# Never run this as the student workflow. Target: Debian bookworm arm64 (Raspberry Pi OS).
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
BUNDLE="$ROOT/offline_bundle"
TARGET_ARCH="${TARGET_ARCH:-arm64}"
TARGET_DISTRO="${TARGET_DISTRO:-bookworm}"

echo "Preparing offline bundle for ${TARGET_DISTRO}/${TARGET_ARCH}"
echo "This step REQUIRES Internet on the developer machine."

mkdir -p \
  "$BUNDLE/deb_packages" \
  "$BUNDLE/python_wheels" \
  "$BUNDLE/source" \
  "$BUNDLE/documentation" \
  "$BUNDLE/datasets" \
  "$BUNDLE/gnuradio" \
  "$BUNDLE/challenge_data" \
  "$BUNDLE/toolchains" \
  "$BUNDLE/examples" \
  "$BUNDLE/manifests"

cat > "$BUNDLE/manifests/target-platform.txt" <<EOF
distro: debian
suite: $TARGET_DISTRO
architecture: $TARGET_ARCH
notes: Raspberry Pi OS / Debian ${TARGET_DISTRO} ${TARGET_ARCH} baseline image
EOF

PKG_LIST="$BUNDLE/manifests/apt-packages.txt"
cat > "$PKG_LIST" <<'EOF'
# Required — Linux baseline
bash
coreutils
util-linux
procps
findutils
grep
sed
gawk
less
file
tree
tar
gzip
xz-utils
zip
unzip
rsync
curl
wget
openssh-server
openssh-client
iproute2
iputils-ping
net-tools
netcat-openbsd
lsof
man-db
manpages
manpages-dev
tmux
vim-tiny
nano

# Required — C/C++ toolchain
build-essential
gcc
g++
libc6-dev
binutils
make
cmake
ninja-build
pkg-config
gdb

# Required — debugging / analysis
strace
ltrace
binutils
bsdmainutils
xxd
valgrind

# Required — git
git

# Required — Python
python3
python3-pip
python3-venv
python3-setuptools
python3-wheel
python3-dev
python3-numpy
python3-scipy
python3-matplotlib
python3-yaml
python3-pytest
python3-pandas

# Required — docs helpers
python3-doc
gcc-doc
glibc-doc
cmake-data

# Strongly recommended — GNU Radio stack (version pins recorded at download time)
gnuradio
gnuradio-dev
gr-osmosdr

# Optional — RTL-SDR hardware track (NOT required for baseline curriculum)
rtl-sdr
librtlsdr-dev
EOF

echo "Wrote $PKG_LIST"

# Download .debs with dependencies if on a matching host; otherwise instruct.
if command -v apt-get >/dev/null && [[ "$(dpkg --print-architecture)" == "$TARGET_ARCH" ]]; then
  echo "Downloading .deb packages via apt-get download ..."
  # shellcheck disable=SC2046
  cd "$BUNDLE/deb_packages"
  grep -vE '^\s*#|^\s*$' "$PKG_LIST" | while read -r pkg; do
    apt-get download "$pkg" || echo "WARN: could not download $pkg"
  done
  # Prefer: apt-rdepends / apt-cache depends for recursive offline sets on a real builder.
  echo "NOTE: For a complete recursive dependency closure, use a chroot/pbuilder matching the Pi."
else
  cat > "$BUNDLE/deb_packages/README.md" <<EOF
# deb_packages

Populate on a Debian ${TARGET_DISTRO} ${TARGET_ARCH} builder (or chroot):

\`\`\`bash
# example recursive fetch pattern
mkdir -p /tmp/academy-debs && cd /tmp/academy-debs
while read pkg; do
  apt-get download \$pkg
done < ../manifests/apt-packages.txt
# then resolve Depends recursively until closure
\`\`\`

Copy resulting \`.deb\` files into this directory before deploying to the Pi.
EOF
fi

# Python wheels (manylinux / linux aarch64)
REQ="$ROOT/python-requirements.txt"
if command -v pip3 >/dev/null; then
  pip3 download -r "$REQ" -d "$BUNDLE/python_wheels" \
    --platform manylinux2014_aarch64 --only-binary=:all: || \
  pip3 download -r "$REQ" -d "$BUNDLE/python_wheels" || \
  echo "WARN: wheel download incomplete — retry on linux/${TARGET_ARCH}"
fi

# Snapshot lockfiles into bundle
cp -a "$ROOT/packages.lock" "$ROOT/python-requirements.txt" "$ROOT/toolchain-manifest.txt" \
  "$BUNDLE/manifests/" 2>/dev/null || true

cat > "$BUNDLE/gnuradio/README.md" <<'EOF'
# GNU Radio offline payload

Baseline curriculum requires GNU Radio + GRC + Python bindings offline.

Recommended approach on a matching Debian arm64 builder:
1. `apt-get download gnuradio gnuradio-dev` (+ recursive deps) into `../deb_packages/`
2. Optionally vendor example flowgraphs into `../examples/gnuradio/`
3. Provide `install_local.sh` that only runs `dpkg -i` on already-copied debs

Optional hardware extras (rtl-sdr) must remain optional.
EOF

cat > "$BUNDLE/documentation/README.md" <<'EOF'
# Offline documentation payload

Copy permitted local HTML/PDF references here (man pages are installed via apt packages).
The academy also ships curated markdown under `/opt/academy/docs`.
EOF

echo
echo "Bundle skeleton ready at $BUNDLE"
echo "Next: complete dependency closure on a matching Pi/chroot, then copy bundle to the Pi and run ./install.sh"
