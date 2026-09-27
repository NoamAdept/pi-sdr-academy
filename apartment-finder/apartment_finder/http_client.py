"""Small HTTP helper. Does not solve captchas or retry past a block."""

from __future__ import annotations

import urllib.error
import urllib.request

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

BLOCK_MARKERS = (
    "radware bot manager",
    "perfdrive.com",
    "cf-browser-verification",
    "<title>access denied",
    "<title>just a moment",
)


class FetchError(Exception):
    def __init__(self, message: str, url: str = ""):
        super().__init__(message)
        self.url = url


def fetch(url: str, timeout: float = 25, max_bytes: int = 2_000_000, user_agent: str = BROWSER_UA) -> tuple[str, str]:
    """Return (body, final_url). Raise FetchError on HTTP errors or bot walls."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            final = response.geturl()
            body = response.read(max_bytes + 1).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise FetchError(f"HTTP {exc.code}", url) from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"connection error: {exc.reason}", url) from exc
    except TimeoutError as exc:
        raise FetchError("timed out", url) from exc
    if status >= 400:
        raise FetchError(f"HTTP {status}", final)
    lowered = body[:4000].lower()
    for marker in BLOCK_MARKERS:
        if marker in lowered:
            raise FetchError(f"bot protection ({marker})", final)
    return body, final
