# Contributing

Thank you for helping keep the academy small, offline, and teachable.

## Ground rules

1. **No network on the student path.** Challenges must run with the offline bundle only.
2. **Keep workspaces clean.** Stage puzzle files, `README.txt`, and real `./run` / `./check` binaries — never drop `BRIEFING.md`, `./submit`, `./hint`, or `./next`.
3. **Do not commit secrets.** Session data, `flag.txt`, unlocked instructor guides, and `.instructor_password` are gitignored for a reason.
4. **Do not leak flags in docs or commit messages.**

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "./platform[dev]"
export ACADEMY_CURRICULUM=$PWD/curriculum
export ACADEMY_DOCS=$PWD/docs
export ACADEMY_DATA=$PWD/.academy-data
make test
```

## Challenge authoring

1. Copy an existing challenge under the right `curriculum/modules/NN-slug/challenges/`.
2. Set a stable `id:` (kebab-case). Keep the folder name equal to the id.
3. Put student files in `files/`. Put graders students must not read in `hidden/`.
4. If setup compiles helpers, do it in `setup.sh` and delete sources you do not want in the workspace.
5. Checkers compare against `expected_answer()` / sealed session data, not a hardcoded submit flag.
6. Add a display title in `platform/academy/ui_flavor.py` if the YAML title is too dry.
7. Run `make test` and play the challenge once from **Start** in the dojo.

Schema: `curriculum/schema/challenge.schema.yaml`.

## Pull requests

- One concern per PR (engine vs curriculum vs docs).
- Update the matching directory README if you change layout or commands.
- Include a short test plan: which challenge you started, checked, and submitted.

## Code style

- Python 3.11+, stdlib where it is enough (the HTTP server is on purpose).
- Match naming already used in the file you touch.
- Prefer small, readable checkers over clever one-liners.
