# Pi SDR Academy

Offline, belt-ranked laboratory for **systems programming → DSP → software-defined radio**.

Students work on a Raspberry Pi (Debian) with no Internet. Challenges are staged locally, graded in the workspace, and scored in a dojo UI modeled on hands-on cyber education platforms.

**151 challenges** across **26 modules**, grouped into core belts (white → black) plus an optional brown-belt qualification track.

## Why this exists

Classroom RF and systems courses usually split theory from practice. This academy keeps both on one machine:

- Terminal-first challenges with a clean workspace (`README.txt`, `./run`, `./check`)
- Session-randomized flags (template answers from the curriculum never score after a start)
- Sequential dojo unlocks — finish a belt to reveal the next
- Air-gapped install path via `offline_bundle/`

Hardware baseline is **Pi + SD card**. RF is simulated in software. An RTL-SDR is optional, never required.

## Quick start (development machine)

Python 3.11+ is required.

```bash
git clone <this-repo>
cd pi-sdr-academy

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ./platform
pip install pytest                 # optional, for tests

export ACADEMY_CURRICULUM=$PWD/curriculum
export ACADEMY_DOCS=$PWD/docs
export ACADEMY_DATA=$PWD/.academy-data

academy                            # welcome + belt map
academy serve --host 127.0.0.1 --port 8080
```

Open [http://127.0.0.1:8080/](http://127.0.0.1:8080/). Use **Start** on a challenge to stage the workspace and open a terminal.

If `academy` is not on `PATH`, run the same commands as `python -m academy`.

Student walkthrough: [GETTING_STARTED.md](GETTING_STARTED.md)  
Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)  
Belts: [docs/dojos.md](docs/dojos.md)

## Everyday loop

```text
Start (dojo UI or `academy next`)
        │
        ▼
  workspace  →  read README.txt  →  solve  →  ./check
        │
        ▼
  Submit in the dojo (paste a found flag, or leave empty after ./check)
```

| Where | What |
|-------|------|
| Dojo UI | Start, Check, Hint, submit flag |
| Workspace | Puzzle files only — `README.txt`, `./run`, `./check` |
| CLI | `academy next`, `academy hint`, `academy submit`, `academy status` |

Do **not** expect `./submit`, `./hint`, or `BRIEFING.md` in the workspace. Those helpers were removed so the dropzone stays clean.

## Repository layout

```text
pi-sdr-academy/
├── curriculum/          Challenges, modules, dojo map
├── platform/            Engine, CLI, HTTP dojo UI
├── docs/                Offline reference + stakeholder materials
├── scripts/             Bundle, verify, instructor lock/unlock
├── instructor/          Encrypted solution guides (password-protected)
├── offline_bundle/      Air-gapped packages + Pi installer
├── python-requirements.txt
├── packages.lock
├── toolchain-manifest.txt
├── GETTING_STARTED.md   Student guide
└── ARCHITECTURE.md      How the platform is put together
```

## Curriculum map

| Belt | Dojo | Modules |
|------|------|---------|
| White | Intro to the Lab | orientation, linux-cli |
| Yellow | Software Craft | python → git-workflow |
| Orange | Systems Core | systems-programming, computer-architecture |
| Green | DSP Foundations | dsp-fundamentals, fft, dsp-filters |
| Blue | Radio Path | iq-sdr → synchronization |
| Purple | Receivers & Radio Security | complete-receivers, protocol-re, sdr-security-ctf |
| Black | Capstone — Blackout | capstone-blackout |
| Brown (side) | Language Qualification | python / C++ / GNU Radio C++ |

Each core module is six challenges (2 easy / 2 medium / 2 hard). Hard challenges are designed to fit in a focused sitting, not a multi-day grind.

## Offline Pi deploy

Developer machine (Internet OK) → student Pi (no Internet):

```text
scripts/prepare_offline_bundle.sh
        │
        ▼
copy repo + offline_bundle/ to the Pi
        │
        ▼
offline_bundle/install.sh
        │
        ▼
scripts/verify_environment.sh
```

Never design a challenge that needs `apt`, `pip`, GitHub, or cloud APIs on the student device.

## Tests

```bash
make test
# or
PYTHONPATH=$PWD/platform ACADEMY_CURRICULUM=$PWD/curriculum \
  python -m pytest platform/tests -q
```

## Instructors

Solution walkthroughs live in `instructor/guides.encrypted`. Unlock them on a staff machine only — see [instructor/README.md](instructor/README.md) and [SECURITY.md](SECURITY.md).

## License

Source and curriculum scaffolding are MIT — see [LICENSE](LICENSE). Keep classroom flags and unlocked instructor guides off public forks.
