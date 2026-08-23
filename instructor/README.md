# Instructor materials

**Do not put unlocked guides on student images.**

Walkthroughs are an AES-256 archive:

| Path | Role |
|------|------|
| `guides.encrypted` | Locked pack — safe in git / on a staff USB |
| `guides/` + `INDEX.md` | Appear only after unlock (gitignored) |
| `.instructor_password` | Local passphrase cache (gitignored) |

## Unlock (staff)

```bash
cd /path/to/pi-sdr-academy
export INSTRUCTOR_PASSWORD='…'    # otherwise you will be prompted
python3 scripts/unlock_instructor_guides.py
```

Then open `instructor/INDEX.md` and `instructor/guides/<module>/<id>.md`.

## Lock (after regenerating)

```bash
python3 scripts/generate_instructor_guides.py
export INSTRUCTOR_PASSWORD='…'
python3 scripts/lock_instructor_guides.py
```

Prefer a password manager over committing any passphrase. Crypto: `openssl enc -aes-256-cbc -pbkdf2 -iter 600000` over a gzip tar of `guides/` + `INDEX.md`.

See [SECURITY.md](../SECURITY.md).
