# Offline bundle

Copied to the Raspberry Pi and installed **without Internet**.

```text
offline_bundle/
├── deb_packages/       .deb files (populate on a builder)
├── python_wheels/      pip wheels
├── source/             rare source tarballs
├── documentation/      extra PDF/HTML references
├── datasets/           shared DSP/IQ datasets
├── gnuradio/           GR helpers + local installer
├── challenge_data/     large payloads kept out of git
├── toolchains/         optional extra compilers
├── examples/           GRC examples, code samples
├── manifests/          locks copied at prepare time
├── logs/               install logs (generated, gitignored)
└── install.sh          Pi-side installer
```

Empty payload directories are tracked with `.gitkeep`. Real `.deb` / `.whl` files stay gitignored.

## Populate (developer, online)

Target: Debian bookworm **arm64** (Pi 4/5 or matching chroot).

```bash
./scripts/prepare_offline_bundle.sh
```

## Install (student Pi, offline)

```bash
./offline_bundle/install.sh
./scripts/verify_environment.sh
```

The installer must not call `apt update` or `pip` against the network.
