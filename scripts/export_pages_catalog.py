#!/usr/bin/env python3
"""Export a flag-free curriculum catalog for GitHub Pages (static browse)."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "platform"))

from academy.dojos import BELT_COLORS, catalog_payload, dojo_detail  # noqa: E402
from academy.engine import AcademyEngine  # noqa: E402


def main() -> int:
    out = ROOT / "site"
    out.mkdir(parents=True, exist_ok=True)
    curriculum = ROOT / "curriculum"
    data = ROOT / ".academy-pages-export"
    data.mkdir(exist_ok=True)

    engine = AcademyEngine(curriculum_root=curriculum, data_dir=data)
    catalog = catalog_payload(engine)

    dojos = []
    for summary in catalog.get("dojos", []):
        detail = dojo_detail(engine, summary["id"]) or {}
        modules = []
        for mod in detail.get("modules_detail") or detail.get("modules") or []:
            # detail may use different key — normalize
            if isinstance(mod, str):
                continue
            chs = []
            for ch in mod.get("challenges") or []:
                chs.append(
                    {
                        "id": ch.get("id"),
                        "title": ch.get("title"),
                        "difficulty": ch.get("difficulty"),
                        "estimated_time": ch.get("estimated_time"),
                        "description": (ch.get("description") or ch.get("mission") or "")[:500],
                    }
                )
            modules.append(
                {
                    "slug": mod.get("slug"),
                    "title": mod.get("title"),
                    "description": (mod.get("description") or "")[:400],
                    "challenges": chs,
                }
            )
        dojos.append(
            {
                "id": summary["id"],
                "title": summary["title"],
                "belt": summary["belt"],
                "belt_label": summary.get("belt_label"),
                "belt_color": summary.get("belt_color") or BELT_COLORS.get(summary["belt"], "#888"),
                "tagline": summary.get("tagline") or summary.get("tagline", ""),
                "kind": summary.get("kind", "core"),
                "modules": summary.get("modules"),
                "challenges": summary.get("challenges"),
                "modules_detail": modules,
            }
        )

    payload = {
        "name": "Pi SDR Academy",
        "tagline": "Offline lab — five belts from shell to IQ. Fifty challenges.",
        "note": "Browse-only on GitHub Pages. Run locally for Start / Check / Submit.",
        "run": {
            "local": "./run.sh",
            "url": "http://127.0.0.1:8080/dojo",
            "admin": "ACADEMY_ADMIN=1 ./run.sh",
        },
        "dojos": dojos,
    }
    (out / "catalog.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    icons_src = ROOT / "platform" / "academy" / "static" / "icons"
    icons_dst = out / "icons"
    if icons_src.is_dir():
        if icons_dst.exists():
            shutil.rmtree(icons_dst)
        shutil.copytree(icons_src, icons_dst)

    print(f"Wrote {out / 'catalog.json'} ({len(dojos)} dojos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
