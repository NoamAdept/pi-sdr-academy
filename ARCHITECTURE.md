# Architecture

Pi SDR Academy is a local, offline challenge engine. Nothing binds outside `127.0.0.1` by default. Progress is JSON on disk. Session flags are minted per start and stored under the data directory, not in the student workspace.

## Runtime

```text
                    Debian / macOS (offline)
                              │
                     ┌────────┴────────┐
                     │                 │
                  Dojo UI            CLI
                  (api.py)         (cli.py)
                     │                 │
                     └────────┬────────┘
                              │
                        AcademyEngine
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
           curriculum      progress        secrets
           (YAML)          (JSON)       (per-start flags)
              │
              ▼
        staged workspace   (/challenge or ~/challenge)
              │
              ▼
         ./check  /  planted flag
```

## Platform (`platform/academy`)

| Module | Role |
|--------|------|
| `engine.py` | Load curriculum, stage workspaces, hints, submit |
| `cli.py` | `academy` / `python -m academy` |
| `api.py` | Stdlib HTTP API + dojo HTML |
| `dojos.py` | Belt map, locks, UI copy |
| `ui_flavor.py` | Display titles + generated challenge thumbnails |
| `secrets.py` | Per-session flags and checker answers |
| `grading.py` | Award sealed flag after a successful check |
| `progress.py` | Solved state, hint levels |
| `paths.py` | Workspace + flag file locations |
| `terminal_launch.py` | Open a cleared terminal on Start |
| `docs_server.py` | Offline docs (`academy docs`) |
| `validation.py` | Flag comparison |

## Curriculum (`curriculum/`)

- `dojos.yaml` — core belts and side quests
- `schema/challenge.schema.yaml` — challenge fields
- `modules/NN-slug/` — `module.yaml` + `challenges/<id>/`

A challenge directory typically contains:

```text
challenge.yaml
files/          # staged into the workspace
setup.sh        # optional, runs at start
hidden/         # checkers that must not ship to the student folder
```

On **Start**, the engine:

1. Clears the workspace
2. Copies `files/`
3. Writes `.challenge` and `.flagpath`
4. Mints a session flag (template from YAML is the checker answer only)
5. Plants the session flag into listed puzzle files
6. Runs `setup.sh` if present

It does **not** install `BRIEFING.md`, `./submit`, `./hint`, or `./next`.

## Scoring

Two student paths, one scoreboard:

1. **Find-style** — recover `flag{…}` from files / env / a service, paste it in the dojo or `academy submit 'flag{…}'`.
2. **Check-style** — fill a report or implement a program, run `./check`. On success the engine awards the session flag and marks the challenge solved. An empty submit in the UI runs the same check.

Checkers must call `expected_answer()` / sealed secrets — never hardcode `flag{…}` as the submit token.

## Offline packaging

- Developer (online): `scripts/prepare_offline_bundle.sh`
- Pi (offline): `offline_bundle/install.sh`
- Pins: `packages.lock`, `python-requirements.txt`, `toolchain-manifest.txt`

See [offline_bundle/README.md](offline_bundle/README.md).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `ACADEMY_CURRICULUM` | Path to `curriculum/` |
| `ACADEMY_DOCS` | Path to `docs/` |
| `ACADEMY_DATA` | Progress + secrets directory |
| `ACADEMY_WORKSPACE` | Staged challenge folder |
| `ACADEMY_FLAG_PATH` | Where awarded flags are written |
| `ACADEMY_OPEN_TERMINAL` | Set to `0` to skip terminal launch |

## Performance (Pi)

Prefer short IQ captures. Python is fine for learning; later modules may use C++ for hot DSP. Avoid multi-GB datasets in the baseline curriculum.
