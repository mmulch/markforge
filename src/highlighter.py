"""Syntax highlighter for Markdown text (dark and light colour schemes)."""

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


def _make_colors(dark: bool) -> dict[str, QTextCharFormat]:
    if dark:
        return {
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
    else:
        return {
            "h1":     _fmt("#0000CC", bold=True),
            "h2":     _fmt("#007070", bold=True),
            "h3":     _fmt("#0070C1", bold=True),
            "bold":   _fmt("#795E26", bold=True),
            "italic": _fmt("#A31515", italic=True),
            "code":   _fmt("#A31515", bg="#f0f0f0"),
            "link":   _fmt("#0563C1"),
            "image":  _fmt("#811F3F"),
            "quote":  _fmt("#008000", italic=True),
            "list":   _fmt("#795E26"),
            "hr":     _fmt("#999999"),
            "fence":  _fmt("#999999"),
            "block":  _fmt("#0070C1", bg="#f0f0f0"),
        }


# Patterns paired with color-map keys (compiled once, reused for both themes)
_PATTERNS: list[tuple[QRegularExpression, str]] = [
    (QRegularExpression(r"^# .+$"),                                  "h1"),
    (QRegularExpression(r"^## .+$"),                                 "h2"),
    (QRegularExpression(r"^#{3,6} .+$"),                             "h3"),
    (QRegularExpression(r"\*\*(?!\s)(?:(?!\*\*).)+\*\*"),            "bold"),
    (QRegularExpression(r"__(?!\s)(?:(?!__).)+__"),                  "bold"),
    (QRegularExpression(r"(?<!\*)\*(?!\s)(?:(?!\*).)+\*(?!\*)"),     "italic"),
    (QRegularExpression(r"(?<!_)_(?!\s)(?:(?!_).)+_(?!_)"),         "italic"),
    (QRegularExpression(r"`[^`]+`"),                                 "code"),
    (QRegularExpression(r"!\[([^\]]*)\]\([^)]*\)"),                  "image"),
    (QRegularExpression(r"\[([^\]]+)\]\([^)]*\)"),                   "link"),
    (QRegularExpression(r"^> .+$"),                                  "quote"),
    (QRegularExpression(r"^\s*[-*+] "),                              "list"),
    (QRegularExpression(r"^\s*\d+\. "),                              "list"),
    (QRegularExpression(r"^[-*_]{3,}\s*$"),                          "hr"),
]

_FENCE_START = QRegularExpression(r"^```\w*$")
_FENCE_END   = QRegularExpression(r"^```\s*$")

_STATE_CODE_BLOCK = 1


class MarkdownHighlighter(QSyntaxHighlighter):
    """Simple Markdown highlighter with fenced code block support."""

    def __init__(self, document) -> None:
        super().__init__(document)
        self._colors = _make_colors(dark=True)
        self._rules = [(pat, self._colors[key]) for pat, key in _PATTERNS]

    def set_theme(self, dark: bool) -> None:
        self._colors = _make_colors(dark=dark)
        self._rules = [(pat, self._colors[key]) for pat, key in _PATTERNS]
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # type: ignore[override]
        prev = self.previousBlockState()

        # ── Fenced Code Block ────────────────────────────────────────────────
        if prev == _STATE_CODE_BLOCK:
            if _FENCE_END.match(text).hasMatch():
                self.setFormat(0, len(text), self._colors["fence"])
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self._colors["block"])
                self.setCurrentBlockState(_STATE_CODE_BLOCK)
            return

        if _FENCE_START.match(text).hasMatch():
            self.setFormat(0, len(text), self._colors["fence"])
            self.setCurrentBlockState(_STATE_CODE_BLOCK)
            return

        self.setCurrentBlockState(0)

        # ── Inline rules ──────────────────────────────────────────────────────
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
