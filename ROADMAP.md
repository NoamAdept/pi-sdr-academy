# Roadmap

## Done

- [x] Challenge engine (CLI, HTTP dojo, progress, session flags)
- [x] Challenge YAML schema + 151 authored challenges
- [x] Belt / dojo map with sequential unlocks
- [x] Clean workspace staging (curriculum files only)
- [x] Dojo UI: start, check, hint, flag submit, generated thumbnails
- [x] Encrypted instructor guides
- [x] Offline bundle layout + install / verify scripts

## Next (optional polish)

- Student images that strip `solution:` fields from YAML
- Deeper GNU Radio-native paths where NumPy is still the fallback
- Classroom progress export / multi-user accounts
- Per-module offline cheat-sheets
- Optional RTL-SDR hardware track that never gates the core belts

## Generators

Curriculum builders live in `scripts/`. Do **not** re-run stub generators over authored challenges.

```text
scripts/build_modules_12_16.py
scripts/build_modules_17_99.py
scripts/generate_curriculum_stubs.py   # legacy — leave authored content alone
```
