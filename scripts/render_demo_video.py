#!/usr/bin/env python3
"""Capture DEMO.html with dense motion samples and stitch into DEMO.mp4."""

from __future__ import annotations

import asyncio
import base64
import json
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEMO = DOCS / "DEMO.html"
OUT_DIR = DOCS / "brief-assets" / "demo-frames"
OUT_MP4 = DOCS / "DEMO.mp4"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9231

# scene -> sample times (seconds after unpause) and frame hold duration
# Dense samples = visible zooms / pans / wave motion in the MP4
SCENE_SAMPLES: dict[int, list[tuple[float, float]]] = {
    0: [  # SDR cold open — many cuts of moving graphs
        (0.4, 0.35),
        (1.0, 0.35),
        (1.7, 0.35),
        (2.5, 0.4),
        (3.4, 0.4),
        (4.4, 0.45),
        (5.5, 0.5),
        (6.6, 0.55),
        (7.6, 0.6),
    ],
    1: [  # title punch
        (0.15, 0.35),
        (0.55, 0.45),
        (1.3, 0.7),
        (2.4, 0.9),
        (3.5, 0.9),
    ],
    2: [  # belt pan
        (0.3, 0.4),
        (1.2, 0.5),
        (2.3, 0.55),
        (3.5, 0.6),
        (4.7, 0.65),
        (5.8, 0.7),
    ],
    3: [  # UI home zoom
        (0.25, 0.4),
        (1.1, 0.7),
        (2.3, 0.85),
        (3.6, 0.9),
        (4.5, 0.7),
    ],
    4: [  # UI detail pan
        (0.25, 0.4),
        (1.1, 0.7),
        (2.3, 0.85),
        (3.6, 0.9),
        (4.5, 0.7),
    ],
    5: [  # terminal
        (0.4, 0.55),
        (1.5, 0.7),
        (2.8, 0.8),
        (4.2, 0.85),
        (5.6, 0.9),
        (7.0, 0.85),
    ],
    6: [  # finale
        (0.2, 0.4),
        (0.8, 0.7),
        (2.0, 1.0),
        (3.4, 1.2),
    ],
}


def wait_devtools(timeout: float = 25.0) -> None:
    url = f"http://127.0.0.1:{PORT}/json/version"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as r:
                json.load(r)
                return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Chrome DevTools not ready")


async def record_frames() -> list[tuple[Path, float]]:
    try:
        import websockets
    except ImportError:
        subprocess.check_call(["python3", "-m", "pip", "install", "--quiet", "websockets"])
        import websockets

    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list") as r:
        tabs = json.load(r)
    page = next(t for t in tabs if t.get("type") == "page")
    ws_url = page["webSocketDebuggerUrl"]

    frames: list[tuple[Path, float]] = []
    async with websockets.connect(ws_url, max_size=40_000_000) as ws:
        msg_id = 0

        async def call(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                raw = json.loads(await ws.recv())
                if raw.get("id") == msg_id:
                    if "error" in raw:
                        raise RuntimeError(raw["error"])
                    return raw.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1280, "height": 720, "deviceScaleFactor": 1, "mobile": False},
        )

        async def shot(name: str) -> Path:
            result = await call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
            path = OUT_DIR / name
            path.write_bytes(base64.b64decode(result["data"]))
            return path

        idx = 0
        for scene, samples in SCENE_SAMPLES.items():
            url = f"file://{DEMO}?record=1&pause=1&scene={scene}"
            await call("Page.navigate", {"url": url})
            await asyncio.sleep(1.0)
            # Unpause so CSS animations + canvas run
            await call(
                "Runtime.evaluate",
                {
                    "expression": f"""
                      (() => {{
                        if (window.__demo) window.__demo.goto({scene});
                        if (window.__demo) window.__demo.play();
                        const btn = document.getElementById('pause');
                        if (btn && btn.textContent === 'Play') btn.click();
                      }})()
                    """
                },
            )
            prev = 0.0
            for t, hold in samples:
                await asyncio.sleep(max(0.05, t - prev))
                prev = t
                path = await shot(f"frame_{idx:03d}.png")
                frames.append((path, hold))
                idx += 1
                print(f"  scene {scene} @ {t:.1f}s → {path.name}", flush=True)
    return frames


def main() -> None:
    if not Path(CHROME).exists():
        raise SystemExit(f"Chrome not found at {CHROME}")
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    chrome = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            "--headless=new",
            "--disable-gpu",
            "--window-size=1280,720",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            f"file://{DEMO}?record=1&pause=1&scene=0",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_devtools()
        time.sleep(0.6)
        print("Capturing motion frames…", flush=True)
        frames = asyncio.run(record_frames())

        concat_lines: list[str] = []
        for path, dur in frames:
            concat_lines.append(f"file '{path}'")
            concat_lines.append(f"duration {dur:.3f}")
        if frames:
            concat_lines.append(f"file '{frames[-1][0]}'")

        list_path = OUT_DIR / "concat.txt"
        list_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

        # Soft cuts between frames via minterpolate-ish: encode at higher fps feel
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-fps_mode",
                "vfr",
                "-vf",
                "scale=1280:720:flags=lanczos,format=yuv420p",
                "-c:v",
                "libx264",
                "-crf",
                "17",
                "-preset",
                "medium",
                "-movflags",
                "+faststart",
                str(OUT_MP4),
            ]
        )
        print(f"Wrote {OUT_MP4} ({OUT_MP4.stat().st_size} bytes, {len(frames)} frames)")
    finally:
        chrome.terminate()
        try:
            chrome.wait(timeout=5)
        except subprocess.TimeoutExpired:
            chrome.kill()


if __name__ == "__main__":
    main()
