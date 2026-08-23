# Scripts

Maintainer tools. Students on a prepared image should not need these.

| Script | When to run | Network |
|--------|-------------|---------|
| `prepare_offline_bundle.sh` | Build `.deb` / wheel payload on a matching Debian host | Yes (developer) |
| `verify_environment.sh` | After Pi install, before class | No |
| `generate_instructor_guides.py` | Rebuild walkthrough markdown from curriculum | No |
| `lock_instructor_guides.py` | Encrypt `instructor/guides/` → `guides.encrypted` | No |
| `unlock_instructor_guides.py` | Staff unlock | No |
| `protect_instructor_guides.py` | Helper around lock / password file | No |
| `seal_flags_in_checkers.py` / `repair_sealed_checkers.py` | Keep graders off hardcoded submit flags | No |
| `build_modules_12_16.py` / `build_modules_17_99.py` | Regenerators for later DSP modules | No |
| `generate_curriculum_stubs.py` | Legacy stubber — **do not** run over authored labs | No |
| `render_demo_video.py` | Rebuild `docs/DEMO.mp4` from `docs/DEMO.html` | No |

```bash
export INSTRUCTOR_PASSWORD='…'
python3 scripts/unlock_instructor_guides.py
```
