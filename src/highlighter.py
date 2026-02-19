"""Syntax-Highlighter für Markdown-Text (VS-Code-Dark+-Farbschema)."""

from __future__ import annotations

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


def _fmt(
    color: str,
    *,
    bold: bool = False,
    italic: bool = False,
    bg: str | None = None,
) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Weight.Bold)
    if italic:
        f.setFontItalic(True)
    if bg:
        f.setBackground(QColor(bg))
    return f


_C = {
    "h1":     _fmt("#569CD6", bold=True),
    "h2":     _fmt("#4EC9B0", bold=True),
    "h3":     _fmt("#9CDCFE", bold=True),
    "bold":   _fmt("#DCDCAA", bold=True),
    "italic": _fmt("#CE9178", italic=True),
    "code":   _fmt("#CE9178", bg="#2a2a2a"),
    "link":   _fmt("#4EC9B0"),
    "image":  _fmt("#C586C0"),
    "quote":  _fmt("#6A9955", italic=True),
    "list":   _fmt("#DCDCAA"),
    "hr":     _fmt("#555555"),
    "fence":  _fmt("#555555"),
    "block":  _fmt("#9CDCFE", bg="#1a1a2e"),
}

# Regeln für einzelne Zeilen: (Muster, Format)
_RULES: list[tuple[QRegularExpression, QTextCharFormat]] = [
    (QRegularExpression(r"^# .+$"),                                  _C["h1"]),
    (QRegularExpression(r"^## .+$"),                                 _C["h2"]),
    (QRegularExpression(r"^#{3,6} .+$"),                             _C["h3"]),
    (QRegularExpression(r"\*\*(?!\s)(?:(?!\*\*).)+\*\*"),            _C["bold"]),
    (QRegularExpression(r"__(?!\s)(?:(?!__).)+__"),                  _C["bold"]),
    (QRegularExpression(r"(?<!\*)\*(?!\s)(?:(?!\*).)+\*(?!\*)"),     _C["italic"]),
    (QRegularExpression(r"(?<!_)_(?!\s)(?:(?!_).)+_(?!_)"),         _C["italic"]),
    (QRegularExpression(r"`[^`]+`"),                                 _C["code"]),
    (QRegularExpression(r"!\[([^\]]*)\]\([^)]*\)"),                  _C["image"]),
    (QRegularExpression(r"\[([^\]]+)\]\([^)]*\)"),                   _C["link"]),
    (QRegularExpression(r"^> .+$"),                                  _C["quote"]),
    (QRegularExpression(r"^\s*[-*+] "),                              _C["list"]),
    (QRegularExpression(r"^\s*\d+\. "),                              _C["list"]),
    (QRegularExpression(r"^[-*_]{3,}\s*$"),                          _C["hr"]),
]

_FENCE_START = QRegularExpression(r"^```\w*$")
_FENCE_END   = QRegularExpression(r"^```\s*$")

_STATE_CODE_BLOCK = 1


class MarkdownHighlighter(QSyntaxHighlighter):
    """Einfacher Markdown-Highlighter mit Unterstützung für Code-Blöcke."""

    def highlightBlock(self, text: str) -> None:  # type: ignore[override]
        prev = self.previousBlockState()

        # ── Fenced Code Block ────────────────────────────────────────────────
        if prev == _STATE_CODE_BLOCK:
            if _FENCE_END.match(text).hasMatch():
                self.setFormat(0, len(text), _C["fence"])
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), _C["block"])
                self.setCurrentBlockState(_STATE_CODE_BLOCK)
            return

        if _FENCE_START.match(text).hasMatch():
            self.setFormat(0, len(text), _C["fence"])
            self.setCurrentBlockState(_STATE_CODE_BLOCK)
            return

        self.setCurrentBlockState(0)

        # ── Inline-Regeln ─────────────────────────────────────────────────────
        for pattern, fmt in _RULES:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
