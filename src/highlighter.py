"""Syntax highlighter for Markdown text (named colour themes)."""

from __future__ import annotations

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat

from spell_checker import spell_check as _spell_check
from themes import EDITOR_THEMES


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


def _make_colors(theme_name: str) -> dict[str, QTextCharFormat]:
    theme = EDITOR_THEMES.get(theme_name, EDITOR_THEMES["VS Code Dark"])
    syntax = theme["syntax"]
    return {
        key: _fmt(fg, bold=bold, italic=italic, bg=bg)
        for key, (fg, bold, italic, bg) in syntax.items()
    }


# Patterns paired with color-map keys (compiled once, reused for all themes)
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

# ── Spell-check patterns ──────────────────────────────────────────────────────
# Words: Latin + Latin-1 Supplement (covers German umlauts, accented chars, ß)
_WORD_RE      = QRegularExpression(r"[A-Za-z\xC0-\xFF]+")
# Regions to skip: inline code spans and bare URLs
_CODE_SPAN_RE = QRegularExpression(r"`[^`]+`")
_URL_RE       = QRegularExpression(r"https?://\S+")

_STATE_CODE_BLOCK = 1


class MarkdownHighlighter(QSyntaxHighlighter):
    """Simple Markdown highlighter with fenced code block support."""

    def __init__(self, document) -> None:
        super().__init__(document)
        self._colors = _make_colors("VS Code Dark")
        self._rules = [(pat, self._colors[key]) for pat, key in _PATTERNS]

    def set_theme(self, theme_name: str) -> None:
        self._colors = _make_colors(theme_name)
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

        # ── Spell check ───────────────────────────────────────────────────────
        sc = _spell_check()
        if sc.enabled:
            # Collect regions to skip (inline code, URLs)
            skip: list[tuple[int, int]] = []
            for pat in (_CODE_SPAN_RE, _URL_RE):
                it2 = pat.globalMatch(text)
                while it2.hasNext():
                    m2 = it2.next()
                    skip.append((m2.capturedStart(), m2.capturedEnd()))

            it3 = _WORD_RE.globalMatch(text)
            while it3.hasNext():
                m3   = it3.next()
                word  = m3.captured(0)
                start = m3.capturedStart()

                if len(word) < 2:
                    continue
                # Skip regions inside inline code or URLs
                if any(s <= start < e for s, e in skip):
                    continue
                # Skip ALL-CAPS abbreviations (URL, API, HTML …)
                if word.isupper():
                    continue
                # Skip words containing digits
                if any(c.isdigit() for c in word):
                    continue

                if not sc.is_ok(word.lower()):
                    # Merge with existing syntax colour, only add underline
                    fmt = self.format(start)
                    fmt.setUnderlineStyle(
                        QTextCharFormat.UnderlineStyle.SpellCheckUnderline
                    )
                    fmt.setUnderlineColor(QColor("#e04040"))
                    self.setFormat(start, len(word), fmt)
