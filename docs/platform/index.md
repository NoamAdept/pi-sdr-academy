# Academy platform

## Student workflow

```bash
academy                 # guide
academy next            # start next challenge (prints full briefing)
eval "$(academy cd)"    # enter workspace
academy hint
academy submit 'flag{...}'
```

See [GETTING_STARTED.md](../../GETTING_STARTED.md).

## CLI reference

| Command | Purpose |
|---------|---------|
| `academy` / `academy help` | Welcome + next-step suggestion |
| `academy next` | Start next unlocked challenge |
| `academy start ID` | Start specific challenge |
| `academy start ID --keep` | Restart without wiping workspace |
| `academy hint` | Next hint (current challenge) |
| `academy submit 'flag{...}'` | Submit flag (current challenge) |
| `academy list [module]` | Browse |
| `academy status` | Progress |
| `academy where` | Workspace path |
| `academy cd` | Shell: `eval "$(academy cd)"` |
| `academy docs` | Offline docs on :8000 |
| `academy serve` | Dojo UI on :8080 |

## Environment variables

| Variable | Purpose |
|----------|---------|
| `ACADEMY_CURRICULUM` | Path to curriculum/ |
| `ACADEMY_DOCS` | Path to docs/ |
| `ACADEMY_DATA` | Progress JSON directory |
| `ACADEMY_WORKSPACE` | Staged challenge folder |
| `ACADEMY_FLAG_PATH` | Awarded flag file |
| `ACADEMY_OPEN_TERMINAL` | Set `0` to skip launching a terminal |

## Challenge YAML

See `curriculum/schema/challenge.schema.yaml`.
