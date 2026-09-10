# Curriculum

Machine-readable lab content for Pi SDR Academy.

## Layout

```text
curriculum/
├── dojos.yaml
├── schema/
│   └── challenge.schema.yaml
└── modules/
    └── NN-slug/
        ├── module.yaml
        └── challenges/
            └── <id>/
                ├── challenge.yaml
                ├── files/          Copied into the student workspace
                ├── hidden/         Graders students must not see
                └── setup.sh        Optional compile / seal step
```

**26 modules**, **151 challenges**.

## Contract

`challenge.yaml` is the source of truth (id, title, difficulty, description, flags, hints, tools).

On Start the engine:

1. Empties the workspace
2. Copies `files/`
3. Runs `setup.sh` if present (`ACADEMY_WORKSPACE`, `ACADEMY_DATA`, `ACADEMY_FLAG_PATH`)
4. Mints a **session flag** — YAML `flags.value` is the checker answer, not the submit token

Ship a complete `README.txt` plus puzzle files. Do not add platform wrappers.

## Dojos

`dojos.yaml` lists belts and module slugs. Later core dojos stay locked until earlier ones are cleared. Brown-belt side quests are optional.

Authoring notes: [CONTRIBUTING.md](../CONTRIBUTING.md).
