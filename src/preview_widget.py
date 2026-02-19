"""HTML-Vorschau für Markdown-Inhalte (GitHub-Dark-Theme)."""

from __future__ import annotations

import os

import markdown
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QColor, QDesktopServices
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

/* ── Aufgabenlisten ── */
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

/* Häkchen via CSS-Pseudoelement */
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

/* Mathematische Formeln */
.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #c9d1d9; }

/* PlantUML-Diagramme */
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
# Wird in den <head> injiziert; MathJax erkennt \(...\) und \[...\]
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

# ── Math-Extraktion ───────────────────────────────────────────────────────────
# Format 1: einzelnes $ auf eigener Zeile  →  Block-Formel
_MATH_SINGLE_BLOCK = _re.compile(r"^\$[ \t]*\n(.*?)\n\$[ \t]*$",
                                  _re.MULTILINE | _re.DOTALL)
# Format 2: $$...$$  →  Block-Formel
_MATH_DOUBLE_BLOCK = _re.compile(r"\$\$(.*?)\$\$", _re.DOTALL)
# Format 3: $...$   →  Inline-Formel  (kein $ oder Zeilenumbruch innen)
_MATH_INLINE       = _re.compile(r"(?<!\$)\$([^$\n]+?)\$(?!\$)")

_MATH_PH = "XMTH{}XMTH"   # Platzhalter-Format


def _extract_math(text: str) -> tuple[str, dict]:
    """Ersetzt Formeln durch Platzhalter, die Markdown nicht verändert."""
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
    """Setzt die extrahierten Formeln als MathJax-Delimiters wieder ein."""
    for key, (content, display) in store.items():
        if display:
            html = html.replace(key,
                f'<div class="math-block">\\[{content}\\]</div>')
        else:
            html = html.replace(key, f'\\({content}\\)')
    return html


# ── Textvorverarbeitung ───────────────────────────────────────────────────────

# Stellt sicher, dass Listen immer von einer Leerzeile eingeleitet werden,
# damit Python-Markdown sie auch ohne explizite Leerzeile erkennt.
_LIST_START  = _re.compile(r"(\S.*\n)([ \t]*[-*+] )", _re.MULTILINE)
_OLIST_START = _re.compile(r"(\S.*\n)([ \t]*\d+\. )", _re.MULTILINE)

# ~~text~~ → <del>text</del>  (nicht über Zeilengrenzen hinweg)
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

# Zeichen, die am URL-Ende abgeschnitten werden
_TRAIL_CHARS = ".,;:!?)"


def _autolink_text(text: str) -> str:
    """Verlinkt nackte URLs und E-Mail-Adressen in einem Text-Node."""
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
    """Wandelt nackte URLs/E-Mails in HTML-Links um, ohne bestehende Tags anzufassen."""
    parts  = _HTML_TAG.split(html)
    tags   = _HTML_TAG.findall(html)
    result = []
    skip   = 0   # Zähler für <a>/<code>/<pre>-Verschachtelungen

    for i, text in enumerate(parts):
        if skip == 0 and text:
            text = _autolink_text(text)
        result.append(text)

        if i < len(tags):
            tag = tags[i]
            result.append(tag)
            tl  = tag.lower()
            # Verschachtelungstiefe verwalten
            if tl.startswith(("<a ", "<a>", "<code", "<pre")):
                skip += 1
            elif tl in ("</a>", "</code>", "</pre>"):
                skip = max(0, skip - 1)

    return "".join(result)


# Ersetzt [ ] / [x] in <li>-Elementen durch gestylte Checkboxen
_TASK_OPEN   = _re.compile(r"<li>\[ \]\s*")
_TASK_CLOSED = _re.compile(r"<li>\[x\]\s*", _re.IGNORECASE)

_CB_OPEN   = '<li class="task-item"><input type="checkbox" disabled> <span>'
_CB_CLOSED = '<li class="task-item done"><input type="checkbox" checked disabled> <span>'
_LI_CLOSE  = "</li>"
_SPAN_CLOSE = "</span></li>"


def _postprocess(html: str) -> str:
    """Wandelt Markdown-Aufgabenlisten in gestylte Checkbox-Elemente um."""
    html = _TASK_OPEN.sub(_CB_OPEN, html)
    html = _TASK_CLOSED.sub(_CB_CLOSED, html)
    # Schließendes </li> nach Task-Items mit </span> ergänzen
    html = _re.sub(r"(<li class=\"task-item[^\"]*\">.*?)</li>",
                   lambda m: m.group(1) + _SPAN_CLOSE,
                   html, flags=_re.DOTALL)
    return html


# ── PlantUML-Extraktion ───────────────────────────────────────────────────────

# Erkennt ```plantuml ... ``` Blöcke (Groß-/Kleinschreibung egal)
_PLANTUML_FENCE = _re.compile(
    r"^```[ \t]*plantuml[ \t]*\n(.*?)\n```[ \t]*$",
    _re.MULTILINE | _re.DOTALL | _re.IGNORECASE,
)
_PUML_PH = "XPUML{}XPUML"   # Platzhalter-Format


def _extract_plantuml(text: str) -> tuple[str, dict]:
    """Ersetzt ```plantuml-Blöcke durch Platzhalter vor der Markdown-Verarbeitung."""
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
    """Ersetzt PlantUML-Platzhalter durch <img>-Tags mit Server-URLs."""
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
    """Wandelt Markdown-Text in ein vollständiges HTML-Dokument um."""
    # PlantUML-Blöcke VOR allem anderen extrahieren
    text, puml_store = _extract_plantuml(text)
    # Formeln VOR der Markdown-Verarbeitung extrahieren, damit _  ^ etc.
    # nicht als Kursiv / Hochstellen interpretiert werden.
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


class _NavigationPage(QWebEnginePage):
    """Leitet externe Links an den Systembrowser weiter.

    Lokale Markdown-Dateien werden per Signal an den Editor weitergegeben.
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

            # Externe URLs → Systembrowser
            if scheme in _EXTERNAL_SCHEMES:
                QDesktopServices.openUrl(url)
                return False

            # Lokale Dateien auswerten
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
    """Zeigt gerendertes Markdown als HTML-Seite an."""

    # Wird ausgelöst, wenn auf einen lokalen Markdown-Link geklickt wird
    open_file = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _HAS_WEBENGINE:
            self._view: QWebEngineView = QWebEngineView()
            self._page = _NavigationPage(self._view)
            self._page.open_file.connect(self.open_file)
            self._view.setPage(self._page)
            self._page.setBackgroundColor(QColor("#0d1117"))
            # Erlaubt file://-Seiten das Laden externer https://-Ressourcen
            # (z. B. PlantUML-Diagramme vom Server, MathJax-CDN)
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

    # ── Öffentliche API ───────────────────────────────────────────────────────

    def set_markdown(self, text: str, base_url: QUrl | None = None) -> None:
        """Rendert *text* als Markdown und aktualisiert die Vorschau.

        *base_url* wird als Basis für relative Pfade (z. B. Bilder) verwendet.
        Fehlt der Parameter, wird das aktuelle Arbeitsverzeichnis genutzt.
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

    # ── Internes (nur WebEngine) ──────────────────────────────────────────────

    def _load_html(self, scroll_y: object) -> None:
        self._scroll_y = float(scroll_y) if isinstance(scroll_y, (int, float)) else 0.0
        self._view.setHtml(self._pending_html, self._base_url)

    def _restore_scroll(self, ok: bool) -> None:
        if ok and self._scroll_y > 0:
            self._view.page().runJavaScript(
                f"window.scrollTo(0, {self._scroll_y});"
            )
