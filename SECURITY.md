# Security

Pi SDR Academy is an **offline teaching lab**, not a networked product. Still treat flags and instructor material as secrets.

## Do not commit

| Path | Why |
|------|-----|
| `.academy-data/` | Student progress + minted session flags |
| `/challenge/`, `~/challenge` | Live workspace |
| `/flag.txt`, `~/flag.txt` | Awarded session flags |
| `instructor/guides/` | Unlocked walkthroughs |
| `instructor/.instructor_password` | Archive passphrase |

The encrypted pack `instructor/guides.encrypted` is safe to keep in git. The password is not.

## Session flags

Each **Start** mints `flag{prefix_<6 hex>}`. The YAML `flags.value` is the **checker answer**, not the submit token. After a start, pasting the template flag must fail.

Checkers that award a flag must read the sealed secret for the current challenge (see `platform/academy/grading.py` and `secrets.py`).

## Instructor guides

Unlock only on staff machines:

```bash
export INSTRUCTOR_PASSWORD='…'
python3 scripts/unlock_instructor_guides.py
```

Do not copy unlocked `instructor/guides/` onto student SD cards.

## Reporting

If a challenge ships a grader, solution, or password in `files/`, treat it as a bug and fix it before class.
