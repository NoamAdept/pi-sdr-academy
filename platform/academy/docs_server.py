"""Minimal offline docs HTTP server (stdlib only)."""

from __future__ import annotations

import html
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


def _md_to_html(text: str) -> str:
    """Tiny markdown subset renderer for offline docs (no external deps)."""
    lines = text.splitlines()
    out: list[str] = []
    in_code = False
    in_ul = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    for line in lines:
        if line.startswith("```"):
            close_ul()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append("<pre><code>")
                in_code = True
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            close_ul()
            level = len(heading.group(1))
            out.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
            continue
        if re.match(r"^[-*]\s+", line):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            item = re.sub(r"^[-*]\s+", "", line)
            out.append(f"<li>{_inline(item)}</li>")
            continue
        close_ul()
        if not line.strip():
            out.append("")
            continue
        out.append(f"<p>{_inline(line)}</p>")
    close_ul()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def _inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


class DocsHandler(SimpleHTTPRequestHandler):
    docs_root: Path = Path(".")

    def translate_path(self, path: str) -> str:
        path = unquote(path.split("?", 1)[0])
        if path in ("/", "/docs", "/docs/"):
            candidate = self.docs_root / "index.md"
            if candidate.exists():
                return str(candidate)
            return str(self.docs_root / "index.html")
        if path.startswith("/docs/"):
            path = path[len("/docs/") :]
        else:
            path = path.lstrip("/")
        full = (self.docs_root / path).resolve()
        if not str(full).startswith(str(self.docs_root.resolve())):
            return str(self.docs_root / "index.md")
        if full.is_dir():
            for name in ("index.md", "index.html", "README.md"):
                cand = full / name
                if cand.exists():
                    return str(cand)
        return str(full)

    def do_GET(self) -> None:  # noqa: N802
        path = Path(self.translate_path(self.path))
        if path.suffix == ".md" and path.exists():
            body = _wrap_html(path.stem, _md_to_html(path.read_text(encoding="utf-8")))
            data = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def log_message(self, fmt: str, *args) -> None:
        # Quiet local logs
        pass


def _wrap_html(title: str, content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)} — Pi SDR Academy Docs</title>
  <style>
    :root {{
      --bg: #0f1419;
      --fg: #e7ecf1;
      --muted: #9aa7b5;
      --accent: #3d9b7a;
      --panel: #1a222c;
      --code: #121820;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif;
      background:
        radial-gradient(1200px 600px at 10% -10%, #1c3a32 0%, transparent 55%),
        radial-gradient(900px 500px at 100% 0%, #243044 0%, transparent 50%),
        var(--bg);
      color: var(--fg);
      line-height: 1.55;
    }}
    header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #2a3542;
      background: color-mix(in srgb, var(--panel) 88%, transparent);
      backdrop-filter: blur(8px);
      position: sticky; top: 0;
    }}
    header a {{ color: var(--accent); text-decoration: none; font-weight: 600; }}
    main {{
      max-width: 860px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    h1,h2,h3 {{ line-height: 1.25; }}
    code, pre {{
      font-family: "IBM Plex Mono", "Source Code Pro", ui-monospace, monospace;
      background: var(--code);
    }}
    code {{ padding: 0.1em 0.35em; border-radius: 4px; }}
    pre {{
      padding: 1rem;
      overflow-x: auto;
      border-radius: 8px;
      border: 1px solid #2a3542;
    }}
    pre code {{ padding: 0; background: transparent; }}
    a {{ color: #7ec8ff; }}
    ul {{ padding-left: 1.25rem; }}
    .muted {{ color: var(--muted); font-size: 0.95rem; }}
  </style>
</head>
<body>
  <header>
    <a href="/docs/">Pi SDR Academy</a>
    <span class="muted"> — offline documentation</span>
  </header>
  <main>
    {content}
  </main>
</body>
</html>
"""


def serve_docs(docs_root: Path, host: str = "127.0.0.1", port: int = 8000) -> None:
    docs_root = docs_root.resolve()
    handler = type("BoundDocsHandler", (DocsHandler,), {"docs_root": docs_root})
    httpd = ThreadingHTTPServer((host, port), handler)
    httpd.serve_forever()
