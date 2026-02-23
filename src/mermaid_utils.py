"""Mermaid diagram rendering via the kroki.io public API.

Diagrams are rendered server-side and returned as PNG data URIs — the same
pattern used for PlantUML.  This avoids the issues with running mermaid.js
inside Qt WebEngine pages loaded via setHtml() (opaque security origin,
sandboxed-iframe rendering in mermaid strict mode, etc.).
"""

from __future__ import annotations

import base64
import urllib.request
import zlib

_KROKI_SERVER = "https://kroki.io"


def _encode(code: str) -> str:
    """Compress with zlib and base64url-encode for a kroki.io GET URL."""
    compressed = zlib.compress(code.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode().rstrip("=")


def png_url(code: str) -> str:
    """Returns the kroki.io URL that renders *code* as a PNG."""
    return f"{_KROKI_SERVER}/mermaid/png/{_encode(code)}"


_png_cache: dict[str, str] = {}


def png_data_uri(code: str) -> str:
    """Fetch a PNG rendering of *code* from kroki.io and return it as a
    data URI for use in an HTML <img> tag.

    Only successful fetches are cached; failures are retried on the next render.
    Returns an empty string if the server cannot be reached.
    """
    if code in _png_cache:
        return _png_cache[code]

    url = png_url(code)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MarkForge"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
        uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        _png_cache[code] = uri
        return uri
    except Exception:
        return ""
