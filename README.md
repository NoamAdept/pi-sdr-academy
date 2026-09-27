# Pi SDR Academy

Offline lab: **five belts · ninety-four challenges · shell → IQ**.
Beginner-friendly White Belt, qualification side paths, progress on git branches.

## Closed network (USB / air-gap)

On any machine that already has **python3** (no pip):

```bash
tar -xzf pi-sdr-academy.tar.gz
cd pi-sdr-academy
./run.sh
```

Open the URL it prints. Read the intro, then **Enter the lab**.

**Start → solve in `./challenge` → Done.**

Build that tarball (online/dev machine once):

```bash
./scripts/pack_portable.sh
# → dist/pi-sdr-academy.tar.gz
```

Copy only that `.tar.gz` onto the closed network. Nothing else to install.

## Same folder, same command

From a git checkout that already includes `vendor/`:

```bash
./run.sh
```

## Layout

```text
run.sh           launcher (python3 only)
curriculum/      94 challenges
platform/        engine + UI
vendor/          pure-Python YAML (no .so)
scripts/         pack + curriculum check
```
