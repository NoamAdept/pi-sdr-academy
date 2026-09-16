# Pi SDR Academy

Offline lab: **five belts · fifty challenges · shell → IQ**.

One loop. No cloud. No pip. Python 3 only.

## Run (the only setup)

From this repo:

```bash
./run.sh
```

Or from the portable pack:

```bash
tar -xzf pi-sdr-academy.tar.gz
cd pi-sdr-academy
./run.sh
```

Open the URL it prints. Then:

1. **Start** — files land in `./challenge`
2. Open that folder, read `README.txt`, solve it
3. **Done** — grades your work

Belts unlock in order. Hints are optional.

## Build the one tarball

```bash
./scripts/pack_portable.sh
# → dist/pi-sdr-academy.tar.gz
```

Copy that file to a USB stick / air-gapped host. Extract and `./run.sh`.

## What you learn

| Belt | Focus |
|------|--------|
| White | Terminal, filesystem, first flags |
| Yellow | Python + C as daily tools |
| Orange | Debugging + systems programming |
| Green | DSP fundamentals + FFT |
| Blue | IQ captures + BPSK |

Workspaces stay clean: `README.txt`, puzzle files, `./run` / `./check` when shipped. No cloud accounts.

## Optional

```bash
ACADEMY_ADMIN=1 ./run.sh   # curriculum writer UI
```

Dev extras (`pip install -e ./platform`, CLI `academy`, full archive under `curriculum-full/`) exist for maintainers — students never need them.
