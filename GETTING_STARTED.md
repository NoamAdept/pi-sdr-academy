# Getting started

This machine is the dojo. You do not need the Internet.

You begin on the **white belt** path. Core dojos unlock in order. Optional brown-belt side quests can be done in parallel once you have the tooling.

Belt map: [docs/dojos.md](docs/dojos.md)

## One-time setup

On a packaged Pi image, `academy` is already on `PATH`. On a laptop:

```bash
source .venv/bin/activate
export ACADEMY_CURRICULUM=$PWD/curriculum
export ACADEMY_DOCS=$PWD/docs
export ACADEMY_DATA=$PWD/.academy-data
pip install -e ./platform
```

The challenge folder is `/challenge` on a prepared Pi, or `~/challenge` on a Mac/Linux laptop.

## Play in the browser (recommended)

```bash
academy serve --host 127.0.0.1 --port 8080
```

Open [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

1. Open a dojo, then a challenge.
2. Click **Start** — a terminal opens in the workspace (scrollback cleared).
3. Read `README.txt`. Use `./run` when the challenge has a helper program.
4. When you think you are done, run `./check` in the terminal **or** click **Check** in the UI.
5. If the challenge plants a `flag{…}`, paste it and click **Go**.  
   If `./check` already succeeded, **Go with an empty box** scores the same way.

Solved challenges show a green flag in the list.

## Play in the terminal

```bash
academy                 # welcome + belt map
academy next            # stage the next unlocked challenge
cd /challenge           # or: cd ~/challenge
cat README.txt
./check                 # grade this challenge
academy hint            # next hint
academy submit          # score after a successful ./check
academy submit 'flag{…}'  # score a flag you found in files
academy status
```

zsh treats `{…}` as a glob. Always quote flags: `'flag{…}'`.

## What belongs in the workspace

| Keep | Do not expect |
|------|----------------|
| `README.txt` | `BRIEFING.md` / extra `README.md` |
| Puzzle files from the challenge | `./submit` `./hint` `./next` |
| `./run` / `./check` when the challenge ships them | Wrapped checkers or academy stubs |

If the folder looks dirty from an older build, **Start** the challenge again. Start always restages a clean copy.

## Offline docs

```bash
academy docs            # http://127.0.0.1:8000/
```

Or browse `docs/` on disk. Start at [docs/index.md](docs/index.md).

## Stuck?

- Take a hint in the UI or `academy hint`.
- Re-read `README.txt` — the mission is there, not in the dojo chrome.
- [docs/troubleshooting/index.md](docs/troubleshooting/index.md)
- Instructors: [instructor/README.md](instructor/README.md) (password-protected guides)
