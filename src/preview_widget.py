"""HTML preview for Markdown content (themed via themes.py)."""

from __future__ import annotations

import os

import markdown
from PyQt6.QtCore import QMarginsF, QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices, QPageLayout, QPageSize
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from themes import PREVIEW_THEMES

try:
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    _HAS_WEBENGINE = True
except Exception as _webengine_err:
    import logging as _logging
    _logging.getLogger(__name__).warning("WebEngine unavailable: %s", _webengine_err)
    _HAS_WEBENGINE = False

try:
    from pygments.formatters import HtmlFormatter as _HF
    _PYGMENTS_CSS = _HF(style="monokai").get_style_defs(".codehilite")
except ImportError:
    _PYGMENTS_CSS = ""

_MD_EXTENSIONS = ["extra", "codehilite", "toc", "sane_lists"]
_MD_EXT_CONFIG = {
    "codehilite": {"noclasses": False, "guess_lang": False},
    "toc":        {"title": "Inhaltsverzeichnis"},
}

import re as _re

try:
    from plantuml_utils import png_data_uri as _plantuml_img
    _HAS_PLANTUML = True
except ImportError:
    _HAS_PLANTUML = False

try:
    from mermaid_utils import png_data_uri as _mermaid_img
    _HAS_MERMAID = True
except ImportError:
    _HAS_MERMAID = False

# ── MathJax ───────────────────────────────────────────────────────────────────
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
_MATH_SINGLE_BLOCK = _re.compile(r"^\$[ \t]*\n(.*?)\n\$[ \t]*$",
                                  _re.MULTILINE | _re.DOTALL)
_MATH_DOUBLE_BLOCK = _re.compile(r"\$\$(.*?)\$\$", _re.DOTALL)
_MATH_INLINE       = _re.compile(r"(?<!\$)\$([^$\n]+?)\$(?!\$)")

_MATH_PH = "XMTH{}XMTH"


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

_LIST_START  = _re.compile(r"(\S.*\n)([ \t]*[-*+] )", _re.MULTILINE)
_OLIST_START = _re.compile(r"(\S.*\n)([ \t]*\d+\. )", _re.MULTILINE)
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
    skip   = 0

    for i, text in enumerate(parts):
        if skip == 0 and text:
            text = _autolink_text(text)
        result.append(text)

        if i < len(tags):
            tag = tags[i]
            result.append(tag)
            tl  = tag.lower()
            if tl.startswith(("<a ", "<a>", "<code", "<pre")):
                skip += 1
            elif tl in ("</a>", "</code>", "</pre>"):
                skip = max(0, skip - 1)

    return "".join(result)


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
    html = _re.sub(r"(<li class=\"task-item[^\"]*\">.*?)</li>",
                   lambda m: m.group(1) + _SPAN_CLOSE,
                   html, flags=_re.DOTALL)
    return html


# ── Mermaid extraction ────────────────────────────────────────────────────────

_MERMAID_FENCE = _re.compile(
    r"^```[ \t]*mermaid[ \t]*\n(.*?)\n```[ \t]*$",
    _re.MULTILINE | _re.DOTALL | _re.IGNORECASE,
)
_MERM_PH = "XMERM{}XMERM"


def _extract_mermaid(text: str) -> tuple[str, dict]:
    """Replaces ```mermaid blocks with placeholders before Markdown processing."""
    store: dict[str, str] = {}
    counter = [0]

    def _replace(m: _re.Match) -> str:
        key = _MERM_PH.format(counter[0])
        store[key] = m.group(1)
        counter[0] += 1
        return f"\n{key}\n"

    text = _MERMAID_FENCE.sub(_replace, text)
    return text, store


def _restore_mermaid(html: str, store: dict) -> str:
    """Replaces Mermaid placeholders with PNG images embedded as data URIs.

    Uses the kroki.io public API for server-side rendering — the same pattern
    as PlantUML.  This avoids all issues with running mermaid.js inside
    Qt WebEngine pages loaded via setHtml() (opaque security origin).
    """
    if not store:
        return html
    for key, diagram_text in store.items():
        if _HAS_MERMAID:
            uri = _mermaid_img(diagram_text)
            if uri:
                replacement = (
                    '<div class="mermaid-diagram">'
                    f'<img src="{uri}" alt="Mermaid diagram"'
                    ' style="max-width:100%;height:auto;"/>'
                    '</div>'
                )
            else:
                replacement = (
                    '<div class="mermaid-diagram">'
                    '<em style="color:#e57373">Mermaid: could not reach server</em>'
                    '</div>'
                )
        else:
            replacement = (
                '<div class="mermaid-diagram">'
                '<em>Mermaid nicht verfügbar</em>'
                '</div>'
            )
        html = html.replace(key, replacement)
    return html


# ── PlantUML extraction ───────────────────────────────────────────────────────

_PLANTUML_FENCE = _re.compile(
    r"^```[ \t]*plantuml[ \t]*\n(.*?)\n```[ \t]*$",
    _re.MULTILINE | _re.DOTALL | _re.IGNORECASE,
)
_PUML_PH = "XPUML{}XPUML"


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
    """Replaces PlantUML placeholders with PNG images embedded as data URIs.

    The PNG is fetched from the PlantUML server in Python and embedded as a
    data:image/png;base64 URI.  This bypasses Qt WebEngine's remote-URL
    restrictions (opaque security origin for setHtml pages) without relying
    on inline SVG, which is unreliable here because the PlantUML server
    embeds non-standard processing instructions inside its SVG output that
    confuse Qt WebEngine's HTML parser.
    """
    if not store:
        return html
    for key, uml_text in store.items():
        if _HAS_PLANTUML:
            uri = _plantuml_img(uml_text)
            if uri:
                replacement = (
                    '<div class="plantuml-diagram">'
                    f'<img src="{uri}" alt="PlantUML diagram"'
                    ' style="max-width:100%;height:auto;"/>'
                    '</div>'
                )
            else:
                replacement = (
                    '<div class="plantuml-diagram">'
                    '<em style="color:#e57373">PlantUML: could not reach server</em>'
                    '</div>'
                )
        else:
            replacement = (
                '<div class="plantuml-diagram">'
                '<em>PlantUML nicht verfügbar</em>'
                '</div>'
            )
        html = html.replace(key, replacement)
    return html


def _render(text: str, theme_name: str = "GitHub Dark") -> str:
    """Converts Markdown text into a complete HTML document."""
    text, puml_store  = _extract_plantuml(text)
    text, merm_store  = _extract_mermaid(text)
    text, math_store  = _extract_math(text)

    body = markdown.markdown(
        _preprocess(text),
        extensions=_MD_EXTENSIONS,
        extension_configs=_MD_EXT_CONFIG,
    )
    body = _restore_math(body, math_store)
    body = _restore_plantuml(body, puml_store)
    body = _restore_mermaid(body, merm_store)
    body = _postprocess(body)
    body = _autolink(body)

    theme_css, _ = PREVIEW_THEMES.get(theme_name, PREVIEW_THEMES["GitHub Dark"])
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        '<meta charset="UTF-8">\n'
        f"<style>\n{theme_css}\n{_PYGMENTS_CSS}\n</style>\n"
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


if _HAS_WEBENGINE:
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

            if scheme in _EXTERNAL_SCHEMES:
                QDesktopServices.openUrl(url)
                return False

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

    open_file = pyqtSignal(str)
    pdf_saved = pyqtSignal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._theme_name = "GitHub Dark"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE:
            self._view: QWebEngineView = QWebEngineView()
            self._page = _NavigationPage(self._view)
            self._page.open_file.connect(self.open_file)
            self._page.pdfPrintingFinished.connect(self._on_pdf_printing_finished)
            self._pdf_export_path = ""
            self._view.setPage(self._page)
            _, bg = PREVIEW_THEMES["GitHub Dark"]
            self._page.setBackgroundColor(QColor(bg))
            self._view.settings().setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
                True,
            )
            self._pending_html = ""
            self._last_md = ""
            self._scroll_y: float = 0.0
            self._view.loadFinished.connect(self._restore_scroll)
        else:
            from PyQt6.QtWidgets import QTextBrowser
            self._view = QTextBrowser()  # type: ignore[assignment]
            self._view.setOpenExternalLinks(True)

        layout.addWidget(self._view)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_markdown(self, text: str, base_url: QUrl | None = None) -> None:
        """Renders *text* as Markdown and updates the preview."""
        self._last_md = text
        html = _render(text, self._theme_name)
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

    def get_html(self) -> str:
        """Return the current document rendered as a complete HTML string."""
        return _render(self._last_md, self._theme_name)

    def set_theme(self, theme_name: str) -> None:
        """Switch preview theme and re-render."""
        self._theme_name = theme_name
        if not _HAS_WEBENGINE:
            return
        _, bg = PREVIEW_THEMES.get(theme_name, PREVIEW_THEMES["GitHub Dark"])
        self._page.setBackgroundColor(QColor(bg))
        if self._pending_html:
            self._view.setHtml(
                _render(self._last_md, theme_name), self._base_url
            )

    def export_to_pdf(self, path: str) -> None:
        """Renders the current preview page as a PDF file at *path*."""
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
