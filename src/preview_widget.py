"""HTML preview for Markdown content (GitHub Dark theme)."""

from __future__ import annotations

import os

import markdown
from PyQt6.QtCore import QMarginsF, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices, QPageLayout, QPageSize
from PyQt6.QtWidgets import QVBoxLayout, QWidget

try:
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False

try:
    from pygments.formatters import HtmlFormatter as _HF
    _PYGMENTS_CSS = _HF(style="monokai").get_style_defs(".codehilite")
except ImportError:
    _PYGMENTS_CSS = ""

_GITHUB_DARK_CSS = """
* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #c9d1d9;
    background-color: #0d1117;
    padding: 24px 48px;
    max-width: 980px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    color: #e6edf3;
    font-weight: 600;
    line-height: 1.25;
    margin-top: 24px;
    margin-bottom: 16px;
    padding-bottom: .3em;
    border-bottom: 1px solid #21262d;
}
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.25em; border-bottom: none; }
h4, h5, h6 { border-bottom: none; }

p { margin: 0 0 16px; }

a { color: #58a6ff; text-decoration: none; }
a:hover { text-decoration: underline; }

code, kbd, samp {
    font-family: "Consolas", "Fira Code", "SFMono-Regular", Menlo, monospace;
    font-size: .875em;
    background-color: rgba(110, 118, 129, .4);
    border-radius: 4px;
    padding: .2em .4em;
    color: #e6edf3;
}

pre {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-size: .875em;
    line-height: 1.45;
    overflow: auto;
    padding: 16px;
    margin: 0 0 16px;
}
pre code {
    background: transparent;
    border: 0;
    font-size: 100%;
    padding: 0;
    white-space: pre;
    color: #e6edf3;
}

blockquote {
    border-left: 4px solid #3d444d;
    color: #848d97;
    margin: 0 0 16px;
    padding: 0 1em;
}
blockquote > :first-child { margin-top: 0; }
blockquote > :last-child  { margin-bottom: 0; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0 0 16px;
}
th, td {
    border: 1px solid #30363d;
    padding: 6px 13px;
    text-align: left;
}
thead tr { background-color: #161b22; font-weight: 600; }
tbody tr:nth-child(odd)  { background-color: #0d1117; }
tbody tr:nth-child(even) { background-color: #161b22; }

hr {
    height: 2px;
    background-color: #21262d;
    border: 0;
    margin: 24px 0;
}

img { max-width: 100%; height: auto; }

ul, ol { padding-left: 2em; margin: 0 0 16px; }
ul { list-style-type: disc; }
ol { list-style-type: decimal; }
ul ul { list-style-type: circle; }
ul ul ul { list-style-type: square; }
li { display: list-item; }
li + li { margin-top: .25em; }
li > p  { margin-top: 16px; }

/* ── Task lists ── */
li.task-item {
    list-style: none !important;
    margin-left: -1.4em;
    display: flex;
    align-items: baseline;
    gap: 0.5em;
}

li.task-item input[type="checkbox"] {
    -webkit-appearance: none;
    appearance: none;
    flex-shrink: 0;
    width: 15px;
    height: 15px;
    margin-top: 3px;
    border: 1.5px solid #444d56;
    border-radius: 3px;
    background-color: #0d1117;
    position: relative;
    cursor: default;
    transition: background-color 0.15s, border-color 0.15s;
}

li.task-item input[type="checkbox"]:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
}

/* Checkmark via CSS pseudo-element */
li.task-item input[type="checkbox"]:checked::after {
    content: "";
    position: absolute;
    left: 4px;
    top: 1px;
    width: 4px;
    height: 8px;
    border: 2px solid #ffffff;
    border-top: none;
    border-left: none;
    transform: rotate(40deg);
}

li.task-item.done > span {
    color: #6e7681;
    text-decoration: line-through;
    text-decoration-color: #444d56;
}

del {
    text-decoration: line-through;
    text-decoration-color: #6e7681;
    color: #6e7681;
}

/* Math formulas */
.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #c9d1d9; }

/* PlantUML diagrams */
.plantuml-diagram {
    text-align: center;
    margin: 20px 0;
}
.plantuml-diagram img {
    max-width: 100%;
    height: auto;
    background: transparent;
}

.footnote { font-size: .875em; color: #848d97; }
"""

_MD_EXTENSIONS = ["extra", "codehilite", "toc", "sane_lists"]
_MD_EXT_CONFIG = {
    "codehilite": {"noclasses": False, "guess_lang": False},
    "toc":        {"title": "Inhaltsverzeichnis"},
}

import re as _re

try:
    from plantuml_utils import svg_url as _plantuml_svg_url
    _HAS_PLANTUML = True
except ImportError:
    _HAS_PLANTUML = False

# ── MathJax ───────────────────────────────────────────────────────────────────
# Injected into <head>; MathJax recognises \(...\) and \[...\]
_MATHJAX_SCRIPT = r"""<script>
MathJax = {
  tex: {
    inlineMath:  [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']]
  },
  options: {
    skipHtmlTags: ['script','noscript','style','textarea','pre','code']
  }
};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>"""

# ── Math extraction ───────────────────────────────────────────────────────────
# Format 1: single $ on its own line  →  display formula
_MATH_SINGLE_BLOCK = _re.compile(r"^\$[ \t]*\n(.*?)\n\$[ \t]*$",
                                  _re.MULTILINE | _re.DOTALL)
# Format 2: $$...$$  →  display formula
_MATH_DOUBLE_BLOCK = _re.compile(r"\$\$(.*?)\$\$", _re.DOTALL)
# Format 3: $...$   →  inline formula  (no $ or newline inside)
_MATH_INLINE       = _re.compile(r"(?<!\$)\$([^$\n]+?)\$(?!\$)")

_MATH_PH = "XMTH{}XMTH"   # placeholder format


def _extract_math(text: str) -> tuple[str, dict]:
    """Replaces math formulas with placeholders that Markdown will not modify."""
    store: dict[str, tuple[str, bool]] = {}

    def _save(content: str, display: bool) -> str:
        key = _MATH_PH.format(len(store))
        store[key] = (content.strip(), display)
        return f"\n{key}\n" if display else key

    text = _MATH_SINGLE_BLOCK.sub(lambda m: _save(m.group(1), True),  text)
    text = _MATH_DOUBLE_BLOCK.sub(lambda m: _save(m.group(1), True),  text)
    text = _MATH_INLINE.sub(      lambda m: _save(m.group(1), False), text)
    return text, store


def _restore_math(html: str, store: dict) -> str:
    """Restores the extracted formulas using MathJax delimiters."""
    for key, (content, display) in store.items():
        if display:
            html = html.replace(key,
                f'<div class="math-block">\\[{content}\\]</div>')
        else:
            html = html.replace(key, f'\\({content}\\)')
    return html


# ── Text pre-processing ───────────────────────────────────────────────────────

# Ensures lists are always preceded by a blank line so Python-Markdown
# recognises them even without an explicit blank line.
_LIST_START  = _re.compile(r"(\S.*\n)([ \t]*[-*+] )", _re.MULTILINE)
_OLIST_START = _re.compile(r"(\S.*\n)([ \t]*\d+\. )", _re.MULTILINE)

# ~~text~~ → <del>text</del>  (single line only)
_STRIKETHROUGH = _re.compile(r"~~([^~\n]+?)~~")


def _preprocess(text: str) -> str:
    text = _STRIKETHROUGH.sub(r"<del>\1</del>", text)
    text = _LIST_START.sub(r"\1\n\2", text)
    text = _OLIST_START.sub(r"\1\n\2", text)
    return text


# ── Autolinks ────────────────────────────────────────────────────────────────

_HTML_TAG       = _re.compile(r"<[^>]+>")
_AUTOLINK_URL   = _re.compile(r"https?://[^\s<>()\[\]\"']+")
_AUTOLINK_EMAIL = _re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Characters stripped from the end of a matched URL
_TRAIL_CHARS = ".,;:!?)"


def _autolink_text(text: str) -> str:
    """Links bare URLs and e-mail addresses within a plain text node."""
    def _url_sub(m: _re.Match) -> str:
        url = m.group().rstrip(_TRAIL_CHARS)
        rest = m.group()[len(url):]
        return f'<a href="{url}">{url}</a>{rest}'

    def _email_sub(m: _re.Match) -> str:
        addr = m.group()
        return f'<a href="mailto:{addr}">{addr}</a>'

    text = _AUTOLINK_URL.sub(_url_sub, text)
    text = _AUTOLINK_EMAIL.sub(_email_sub, text)
    return text


def _autolink(html: str) -> str:
    """Converts bare URLs/e-mails to HTML links without touching existing tags."""
    parts  = _HTML_TAG.split(html)
    tags   = _HTML_TAG.findall(html)
    result = []
    skip   = 0   # nesting counter for <a>/<code>/<pre>

    for i, text in enumerate(parts):
        if skip == 0 and text:
            text = _autolink_text(text)
        result.append(text)

        if i < len(tags):
            tag = tags[i]
            result.append(tag)
            tl  = tag.lower()
            # Track nesting depth
            if tl.startswith(("<a ", "<a>", "<code", "<pre")):
                skip += 1
            elif tl in ("</a>", "</code>", "</pre>"):
                skip = max(0, skip - 1)

    return "".join(result)


# Replaces [ ] / [x] in <li> elements with styled checkboxes
_TASK_OPEN   = _re.compile(r"<li>\[ \]\s*")
_TASK_CLOSED = _re.compile(r"<li>\[x\]\s*", _re.IGNORECASE)

_CB_OPEN   = '<li class="task-item"><input type="checkbox" disabled> <span>'
_CB_CLOSED = '<li class="task-item done"><input type="checkbox" checked disabled> <span>'
_LI_CLOSE  = "</li>"
_SPAN_CLOSE = "</span></li>"


def _postprocess(html: str) -> str:
    """Converts Markdown task lists into styled checkbox elements."""
    html = _TASK_OPEN.sub(_CB_OPEN, html)
    html = _TASK_CLOSED.sub(_CB_CLOSED, html)
    # Replace closing </li> in task items with </span></li>
    html = _re.sub(r"(<li class=\"task-item[^\"]*\">.*?)</li>",
                   lambda m: m.group(1) + _SPAN_CLOSE,
                   html, flags=_re.DOTALL)
    return html


# ── PlantUML-Extraktion ───────────────────────────────────────────────────────

# Matches ```plantuml ... ``` blocks (case-insensitive)
_PLANTUML_FENCE = _re.compile(
    r"^```[ \t]*plantuml[ \t]*\n(.*?)\n```[ \t]*$",
    _re.MULTILINE | _re.DOTALL | _re.IGNORECASE,
)
_PUML_PH = "XPUML{}XPUML"   # Platzhalter-Format


def _extract_plantuml(text: str) -> tuple[str, dict]:
    """Replaces ```plantuml blocks with placeholders before Markdown processing."""
    store: dict[str, str] = {}
    counter = [0]

    def _replace(m: _re.Match) -> str:
        key = _PUML_PH.format(counter[0])
        store[key] = m.group(1)
        counter[0] += 1
        return f"\n{key}\n"

    text = _PLANTUML_FENCE.sub(_replace, text)
    return text, store


def _restore_plantuml(html: str, store: dict) -> str:
    """Replaces PlantUML placeholders with <img> tags pointing to the server URL."""
    if not store:
        return html
    for key, uml_text in store.items():
        if _HAS_PLANTUML:
            url = _plantuml_svg_url(uml_text)
            replacement = (
                f'<div class="plantuml-diagram">'
                f'<img src="{url}" alt="PlantUML-Diagramm">'
                f'</div>'
            )
        else:
            replacement = (
                '<div class="plantuml-diagram">'
                '<em>PlantUML nicht verfügbar</em>'
                '</div>'
            )
        html = html.replace(key, replacement)
    return html


def _render(text: str) -> str:
    """Converts Markdown text into a complete HTML document."""
    # Extract PlantUML blocks before everything else
    text, puml_store = _extract_plantuml(text)
    # Extract math formulas before Markdown processing so that _ ^ etc.
    # are not interpreted as italic / superscript.
    text, math_store = _extract_math(text)

    body = markdown.markdown(
        _preprocess(text),
        extensions=_MD_EXTENSIONS,
        extension_configs=_MD_EXT_CONFIG,
    )
    body = _restore_math(body, math_store)
    body = _restore_plantuml(body, puml_store)
    body = _postprocess(body)
    body = _autolink(body)
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="UTF-8">\n'
        f"<style>\n{_GITHUB_DARK_CSS}\n{_PYGMENTS_CSS}\n</style>\n"
        f"{_MATHJAX_SCRIPT}\n"
        f"</head>\n<body>\n{body}\n</body>\n</html>"
    )


_EXTERNAL_SCHEMES = {"http", "https", "ftp", "ftps", "mailto"}
_BROWSER_EXTS     = {".html", ".htm", ".pdf"}
_MARKDOWN_EXTS    = {".md", ".markdown", ".txt"}


_PDF_CSS_INJECT = """
(function() {
    var s = document.createElement('style');
    s.id = '__pdf_override__';
    s.textContent =
        'body{background:#fff!important;color:#1a1a1a!important}' +
        'h1,h2,h3,h4,h5,h6{color:#1a1a1a!important;border-bottom-color:#ddd!important}' +
        'code,kbd,samp{background:#f0f0f0!important;color:#1a1a1a!important}' +
        'pre{background:#f6f8fa!important;border-color:#ddd!important}' +
        'pre code{color:#1a1a1a!important;background:transparent!important}' +
        'blockquote{color:#555!important;border-left-color:#ccc!important}' +
        'a{color:#0366d6!important}' +
        'th,td{border-color:#ddd!important}' +
        'thead tr{background:#f6f8fa!important}' +
        'tbody tr:nth-child(odd){background:#fff!important}' +
        'tbody tr:nth-child(even){background:#f6f8fa!important}' +
        'hr{background:#ddd!important}';
    document.head.appendChild(s);
})();
"""

_PDF_CSS_REMOVE = """
(function() {
    var s = document.getElementById('__pdf_override__');
    if (s) s.parentNode.removeChild(s);
})();
"""


class _NavigationPage(QWebEnginePage):
    """Redirects external links to the system browser.

    Local Markdown files are forwarded to the editor via a signal.
    """

    open_file = pyqtSignal(str)

    def acceptNavigationRequest(
        self,
        url: QUrl,
        nav_type: QWebEnginePage.NavigationType,
        is_main_frame: bool,
    ) -> bool:
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            scheme = url.scheme().lower()

            # External URLs → system browser
            if scheme in _EXTERNAL_SCHEMES:
                QDesktopServices.openUrl(url)
                return False

            # Evaluate local files
            if url.isLocalFile():
                path = url.toLocalFile()
                ext  = os.path.splitext(path)[1].lower()
                if ext in _BROWSER_EXTS:
                    QDesktopServices.openUrl(url)
                    return False
                if ext in _MARKDOWN_EXTS:
                    self.open_file.emit(path)
                    return False

        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class PreviewWidget(QWidget):
    """Displays rendered Markdown as an HTML page."""

    # Emitted when a local Markdown link is clicked
    open_file = pyqtSignal(str)
    # Emitted when printToPdf finishes: (file_path, success)
    pdf_saved = pyqtSignal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE:
            self._view: QWebEngineView = QWebEngineView()
            self._page = _NavigationPage(self._view)
            self._page.open_file.connect(self.open_file)
            self._page.pdfPrintingFinished.connect(self._on_pdf_printing_finished)
            self._pdf_export_path = ""
            self._view.setPage(self._page)
            self._page.setBackgroundColor(QColor("#0d1117"))
            # Allow file:// pages to load external https:// resources
            # (e.g. PlantUML diagrams from the server, MathJax CDN)
            self._view.settings().setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
                True,
            )
            self._pending_html = ""
            self._scroll_y: float = 0.0
            self._view.loadFinished.connect(self._restore_scroll)
        else:
            from PyQt6.QtWidgets import QTextBrowser
            self._view = QTextBrowser()  # type: ignore[assignment]
            self._view.setOpenExternalLinks(True)

        layout.addWidget(self._view)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_markdown(self, text: str, base_url: QUrl | None = None) -> None:
        """Renders *text* as Markdown and updates the preview.

        *base_url* is used as the base for resolving relative paths (e.g. images).
        If omitted, the current working directory is used.
        """
        html = _render(text)
        if _HAS_WEBENGINE:
            self._pending_html = html
            self._base_url     = base_url or QUrl.fromLocalFile(
                __import__("os").getcwd() + "/"
            )
            self._view.page().runJavaScript(
                "window.scrollY || 0",
                self._load_html,
            )
        else:
            self._view.setHtml(html)  # type: ignore[attr-defined]

    def export_to_pdf(self, path: str) -> None:
        """Renders the current preview page as a PDF file at *path*.

        Temporarily injects a light CSS override so the PDF has a white
        background instead of the dark editor theme.
        """
        if not _HAS_WEBENGINE:
            return
        self._pdf_export_path = path
        self._page.runJavaScript(_PDF_CSS_INJECT, self._after_css_inject)

    # ── Internal (WebEngine only) ─────────────────────────────────────────────

    def _after_css_inject(self, _result: object) -> None:
        layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(15, 15, 15, 15),
            QPageLayout.Unit.Millimeter,
        )
        self._page.printToPdf(self._pdf_export_path, layout)

    def _on_pdf_printing_finished(self, path: str, success: bool) -> None:
        self._page.runJavaScript(_PDF_CSS_REMOVE)
        self.pdf_saved.emit(path, success)

    def _load_html(self, scroll_y: object) -> None:
        self._scroll_y = float(scroll_y) if isinstance(scroll_y, (int, float)) else 0.0
        self._view.setHtml(self._pending_html, self._base_url)

    def _restore_scroll(self, ok: bool) -> None:
        if ok and self._scroll_y > 0:
            self._view.page().runJavaScript(
                f"window.scrollTo(0, {self._scroll_y});"
            )
