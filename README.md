# Pi SDR Academy

Offline lab: **five belts · fifty challenges · shell → IQ**.

```bash
./run.sh
```

Open the URL. Then: **Start → solve in `./challenge` → Done**.

## Portable pack

```bash
./scripts/pack_portable.sh
tar -xzf dist/pi-sdr-academy.tar.gz
cd pi-sdr-academy && ./run.sh
```

Needs **python3** only. No pip. No internet.

## Layout

```text
run.sh           launcher
curriculum/      50 challenges
platform/        engine + UI
vendor/          pure-Python YAML
scripts/         pack + curriculum check
```

## Belts

| Belt | Focus |
|------|--------|
| White | Terminal + first flags |
| Yellow | Python + C |
| Orange | Debugging + systems |
| Green | DSP + FFT |
| Blue | IQ + BPSK |
