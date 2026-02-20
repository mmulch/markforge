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


_png_cache: dict[str, str] = {}


def png_data_uri(text: str) -> str:
    """Fetch the PNG for *text* from the PlantUML server and return it as a
    data URI suitable for use in an HTML <img> tag.

    Why PNG data URI instead of inline SVG or a remote <img> tag:
    - Qt WebEngine blocks remote HTTPS <img> in pages loaded via setHtml()
      (opaque security origin in modern Chromium).
    - Inline SVG is unreliable in this context: the PlantUML server embeds
      non-standard processing instructions (<?plantuml-src …?>) inside the
      SVG element itself, which interfere with Qt WebEngine's HTML parser and
      cause the SVG text nodes to appear as plain text instead of graphics.
    - PNG is binary — no XML/PI parsing involved.  A data:image/png;base64
      URI is resolved locally by the browser and never hits the network, so
      it is not subject to the opaque-origin remote-resource restriction.

    Only successful fetches are cached; failures are retried on the next render.
    Returns an empty string if the server cannot be reached.
    """
    if text in _png_cache:
        return _png_cache[text]

    url = png_url(text)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MarkForge"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
        uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        _png_cache[text] = uri
        return uri
    except Exception:
        return ""
