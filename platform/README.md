# Platform

Python package `academy` — challenge engine, CLI, and local dojo UI.

## Install

From the repository root:

```bash
pip install -e ./platform
```

Requires Python 3.11+ and PyYAML. DSP challenges also need the stack in `python-requirements.txt` (or the offline wheel cache).

## Commands

| Command | Purpose |
|---------|---------|
| `academy` | Welcome + belt map |
| `academy next` | Stage the next unlocked challenge |
| `academy start <id>` | Stage a specific challenge |
| `academy hint [id]` | Reveal the next hint |
| `academy submit ['flag{…}']` | Score a flag, or run workspace `./check` if omitted |
| `academy list [module]` | Browse modules / dojos |
| `academy status` | Progress |
| `academy where` | Print workspace path |
| `eval "$(academy cd)"` | `cd` into the workspace |
| `academy serve` | Dojo UI (default `127.0.0.1:8080`) |
| `academy docs` | Offline docs (default `127.0.0.1:8000`) |

`next`, `hint`, `submit`, `status`, and `dojos` are also installed as short console scripts.

## Package map

```text
platform/academy/
├── engine.py             Load + stage + submit
├── cli.py                Argument parser
├── api.py                HTTP API + static dojo
├── dojos.py              Belt progression
├── ui_flavor.py          Display titles + SVG thumbs
├── secrets.py            Session flags
├── grading.py            Award sealed flag
├── progress.py           JSON progress store
├── paths.py              Workspace / flag locations
├── terminal_launch.py    Open a cleared terminal
├── docs_server.py        Markdown docs server
└── static/dojo.html      Dojo UI
```

## Tests

From the repository root:

```bash
make test
```

## Environment

| Variable | Default |
|----------|---------|
| `ACADEMY_CURRICULUM` | `<repo>/curriculum` |
| `ACADEMY_DATA` | `~/.academy` |
| `ACADEMY_DOCS` | `<repo>/docs` |
| `ACADEMY_WORKSPACE` | `/challenge` then `~/challenge` |
| `ACADEMY_FLAG_PATH` | `/home/flag.txt` then `~/flag.txt` |
| `ACADEMY_OPEN_TERMINAL` | `1` |
