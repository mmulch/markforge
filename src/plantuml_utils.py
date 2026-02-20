"""PlantUML encoding, URL generation, and SVG fetching for the online rendering service."""

from __future__ import annotations

import base64
import urllib.request
import zlib
from functools import lru_cache

PLANTUML_SERVER = "https://www.plantuml.com/plantuml"

# PlantUML verwendet ein eigenes 6-Bit-Encoding mit diesem Alphabet (≠ Base64)
_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def _enc6(b: int) -> str:
    return _CHARS[b & 0x3F]


def _enc3bytes(b1: int, b2: int, b3: int) -> str:
    """Kodiert 3 Bytes als 4 Zeichen des PlantUML-Alphabets."""
    return (
        _enc6(b1 >> 2)
        + _enc6(((b1 & 0x3) << 4) | (b2 >> 4))
        + _enc6(((b2 & 0xF) << 2) | (b3 >> 6))
        + _enc6(b3 & 0x3F)
    )


def _encode_bytes(data: bytes) -> str:
    """Wendet das PlantUML 6-Bit-Encoding auf rohe Bytes an."""
    result = []
    n = len(data)
    i = 0
    while i < n:
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < n else 0
        b3 = data[i + 2] if i + 2 < n else 0
        enc = _enc3bytes(b1, b2, b3)
        rem = n - i
        if rem >= 3:
            result.append(enc)
        elif rem == 2:
            result.append(enc[:3])
        else:
            result.append(enc[:2])
        i += 3
    return "".join(result)


def encode(text: str) -> str:
    """Kodiert PlantUML-Quelltext für die Verwendung in Server-URLs.

    Algorithmus: UTF-8 → raw DEFLATE (kein zlib-Header) → PlantUML-Encoding.
    """
    data = text.encode("utf-8")
    obj = zlib.compressobj(6, zlib.DEFLATED, -15)   # -15 → raw DEFLATE
    compressed = obj.compress(data) + obj.flush()
    return _encode_bytes(compressed)


def svg_url(text: str) -> str:
    """Returns the PlantUML server URL for an SVG rendering."""
    return f"{PLANTUML_SERVER}/svg/{encode(text)}"


def png_url(text: str) -> str:
    """Returns the PlantUML server URL for a PNG rendering."""
    return f"{PLANTUML_SERVER}/png/{encode(text)}"


_svg_cache: dict[str, str] = {}

def svg_inline(text: str) -> str:
    """Fetch the SVG for *text* from the PlantUML server and return it as an
    inline SVG string ready to embed directly in HTML.

    Only successful fetches are cached — failures are retried on the next render.

    Why inline SVG instead of a data URI or remote <img> tag:
    - Qt WebEngine blocks remote HTTPS <img> in pages loaded via setHtml()
      (opaque security origin in modern Chromium).
    - The PlantUML server prefixes its SVG with a non-standard processing
      instruction (<?plantuml ...?>) which causes Chromium to abort parsing
      when the content is delivered as a data:image/svg+xml URI.
    - Embedding the SVG directly in the HTML lets the HTML parser handle it;
      unknown processing instructions are silently ignored.

    Returns an empty string if the server cannot be reached.
    """
    if text in _svg_cache:
        return _svg_cache[text]

    url = svg_url(text)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MarkForge"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Strip any leading processing instructions (<?plantuml …?>, <?xml …?>)
        # so the inline SVG starts cleanly with <svg …>.
        import re as _re
        raw = _re.sub(r"<\?[^>]*\?>", "", raw).strip()
        _svg_cache[text] = raw
        return raw
    except Exception:
        return ""
