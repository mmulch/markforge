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


@lru_cache(maxsize=64)
def svg_data_uri(text: str) -> str:
    """Fetch the SVG for *text* from the PlantUML server and return it as a data URI.

    The result is cached per session so each unique diagram is only fetched once.
    Embedding the SVG as a data URI avoids Qt WebEngine's remote-URL restrictions
    that can block <img> tags pointing at external HTTPS servers when the page is
    loaded via setHtml() (which creates an opaque/null security origin in modern
    Chromium-based engines).

    Returns an empty string if the server cannot be reached.
    """
    url = svg_url(text)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MarkForge"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""
