"""Central theme definitions for MarkForge.

All colour data lives here; other modules import from this module
instead of hard-coding colours.
"""

from __future__ import annotations

# ── Editor Themes ─────────────────────────────────────────────────────────────
# Each entry:
#   "bg", "fg"           – editor background / foreground
#   "gutter_bg/fg"       – line-number gutter colours
#   "line_hl"            – current-line highlight colour
#   "syntax"             – dict[key] = (fg_hex, bold, italic, bg_hex | None)

EDITOR_THEMES: dict[str, dict] = {
    "VS Code Dark": {
        "bg": "#1e1e1e", "fg": "#d4d4d4",
        "gutter_bg": "#252526", "gutter_fg": "#858585", "line_hl": "#2a2a2a",
        "syntax": {
            "h1":     ("#569CD6", True,  False, None),
            "h2":     ("#4EC9B0", True,  False, None),
            "h3":     ("#9CDCFE", True,  False, None),
            "bold":   ("#DCDCAA", True,  False, None),
            "italic": ("#CE9178", False, True,  None),
            "code":   ("#CE9178", False, False, "#2a2a2a"),
            "link":   ("#4EC9B0", False, False, None),
            "image":  ("#C586C0", False, False, None),
            "quote":  ("#6A9955", False, True,  None),
            "list":   ("#DCDCAA", False, False, None),
            "hr":     ("#555555", False, False, None),
            "fence":  ("#555555", False, False, None),
            "block":  ("#9CDCFE", False, False, "#1a1a2e"),
        },
    },
    "VS Code Light": {
        "bg": "#ffffff", "fg": "#1e1e1e",
        "gutter_bg": "#f0f0f0", "gutter_fg": "#888888", "line_hl": "#e8f2ff",
        "syntax": {
            "h1":     ("#0000CC", True,  False, None),
            "h2":     ("#007070", True,  False, None),
            "h3":     ("#0070C1", True,  False, None),
            "bold":   ("#795E26", True,  False, None),
            "italic": ("#A31515", False, True,  None),
            "code":   ("#A31515", False, False, "#f0f0f0"),
            "link":   ("#0563C1", False, False, None),
            "image":  ("#811F3F", False, False, None),
            "quote":  ("#008000", False, True,  None),
            "list":   ("#795E26", False, False, None),
            "hr":     ("#999999", False, False, None),
            "fence":  ("#999999", False, False, None),
            "block":  ("#0070C1", False, False, "#f0f0f0"),
        },
    },
    "Monokai": {
        "bg": "#272822", "fg": "#f8f8f2",
        "gutter_bg": "#3e3d32", "gutter_fg": "#75715e", "line_hl": "#3e3d32",
        "syntax": {
            "h1":     ("#f92672", True,  False, None),
            "h2":     ("#a6e22e", True,  False, None),
            "h3":     ("#66d9e8", True,  False, None),
            "bold":   ("#e6db74", True,  False, None),
            "italic": ("#fd971f", False, True,  None),
            "code":   ("#fd971f", False, False, "#3e3d32"),
            "link":   ("#66d9e8", False, False, None),
            "image":  ("#ae81ff", False, False, None),
            "quote":  ("#75715e", False, True,  None),
            "list":   ("#e6db74", False, False, None),
            "hr":     ("#75715e", False, False, None),
            "fence":  ("#75715e", False, False, None),
            "block":  ("#f8f8f2", False, False, "#3e3d32"),
        },
    },
    "Solarized Dark": {
        "bg": "#002b36", "fg": "#839496",
        "gutter_bg": "#073642", "gutter_fg": "#586e75", "line_hl": "#073642",
        "syntax": {
            "h1":     ("#268bd2", True,  False, None),
            "h2":     ("#2aa198", True,  False, None),
            "h3":     ("#859900", True,  False, None),
            "bold":   ("#b58900", True,  False, None),
            "italic": ("#cb4b16", False, True,  None),
            "code":   ("#dc322f", False, False, "#073642"),
            "link":   ("#2aa198", False, False, None),
            "image":  ("#d33682", False, False, None),
            "quote":  ("#586e75", False, True,  None),
            "list":   ("#b58900", False, False, None),
            "hr":     ("#586e75", False, False, None),
            "fence":  ("#586e75", False, False, None),
            "block":  ("#839496", False, False, "#073642"),
        },
    },
    "Solarized Light": {
        "bg": "#fdf6e3", "fg": "#657b83",
        "gutter_bg": "#eee8d5", "gutter_fg": "#93a1a1", "line_hl": "#eee8d5",
        "syntax": {
            "h1":     ("#268bd2", True,  False, None),
            "h2":     ("#2aa198", True,  False, None),
            "h3":     ("#859900", True,  False, None),
            "bold":   ("#b58900", True,  False, None),
            "italic": ("#cb4b16", False, True,  None),
            "code":   ("#dc322f", False, False, "#eee8d5"),
            "link":   ("#2aa198", False, False, None),
            "image":  ("#d33682", False, False, None),
            "quote":  ("#93a1a1", False, True,  None),
            "list":   ("#b58900", False, False, None),
            "hr":     ("#93a1a1", False, False, None),
            "fence":  ("#93a1a1", False, False, None),
            "block":  ("#657b83", False, False, "#eee8d5"),
        },
    },
    "Nord": {
        "bg": "#2e3440", "fg": "#d8dee9",
        "gutter_bg": "#3b4252", "gutter_fg": "#4c566a", "line_hl": "#3b4252",
        "syntax": {
            "h1":     ("#88c0d0", True,  False, None),
            "h2":     ("#81a1c1", True,  False, None),
            "h3":     ("#5e81ac", True,  False, None),
            "bold":   ("#ebcb8b", True,  False, None),
            "italic": ("#d08770", False, True,  None),
            "code":   ("#bf616a", False, False, "#3b4252"),
            "link":   ("#88c0d0", False, False, None),
            "image":  ("#b48ead", False, False, None),
            "quote":  ("#4c566a", False, True,  None),
            "list":   ("#ebcb8b", False, False, None),
            "hr":     ("#4c566a", False, False, None),
            "fence":  ("#4c566a", False, False, None),
            "block":  ("#d8dee9", False, False, "#3b4252"),
        },
    },
}

# ── Preview Theme CSS ─────────────────────────────────────────────────────────

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

.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #c9d1d9; }

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

_GITHUB_LIGHT_CSS = """
* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #1f2328;
    background-color: #ffffff;
    padding: 24px 48px;
    max-width: 980px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    color: #1f2328;
    font-weight: 600;
    line-height: 1.25;
    margin-top: 24px;
    margin-bottom: 16px;
    padding-bottom: .3em;
    border-bottom: 1px solid #d1d9e0;
}
h1 { font-size: 2em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.25em; border-bottom: none; }
h4, h5, h6 { border-bottom: none; }

p { margin: 0 0 16px; }

a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }

code, kbd, samp {
    font-family: "Consolas", "Fira Code", "SFMono-Regular", Menlo, monospace;
    font-size: .875em;
    background-color: rgba(175, 184, 193, .2);
    border-radius: 4px;
    padding: .2em .4em;
    color: #1f2328;
}

pre {
    background-color: #f6f8fa;
    border: 1px solid #d1d9e0;
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
    color: #1f2328;
}

blockquote {
    border-left: 4px solid #d1d9e0;
    color: #59636e;
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
    border: 1px solid #d1d9e0;
    padding: 6px 13px;
    text-align: left;
}
thead tr { background-color: #f6f8fa; font-weight: 600; }
tbody tr:nth-child(odd)  { background-color: #ffffff; }
tbody tr:nth-child(even) { background-color: #f6f8fa; }

hr {
    height: 2px;
    background-color: #d1d9e0;
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
    border: 1.5px solid #9aa1a9;
    border-radius: 3px;
    background-color: #ffffff;
    position: relative;
    cursor: default;
    transition: background-color 0.15s, border-color 0.15s;
}

li.task-item input[type="checkbox"]:checked {
    background-color: #0969da;
    border-color: #0969da;
}

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
    color: #59636e;
    text-decoration: line-through;
    text-decoration-color: #9aa1a9;
}

del {
    text-decoration: line-through;
    text-decoration-color: #9aa1a9;
    color: #59636e;
}

.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #1f2328; }

.plantuml-diagram {
    text-align: center;
    margin: 20px 0;
}
.plantuml-diagram img {
    max-width: 100%;
    height: auto;
    background: transparent;
}

.footnote { font-size: .875em; color: #59636e; }
"""

_SOLARIZED_DARK_CSS = """
* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #839496;
    background-color: #002b36;
    padding: 24px 48px;
    max-width: 980px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    color: #93a1a1;
    font-weight: 600;
    line-height: 1.25;
    margin-top: 24px;
    margin-bottom: 16px;
    padding-bottom: .3em;
    border-bottom: 1px solid #073642;
}
h1 { font-size: 2em; color: #268bd2; }
h2 { font-size: 1.5em; color: #2aa198; }
h3 { font-size: 1.25em; border-bottom: none; color: #859900; }
h4, h5, h6 { border-bottom: none; }

p { margin: 0 0 16px; }

a { color: #2aa198; text-decoration: none; }
a:hover { text-decoration: underline; }

code, kbd, samp {
    font-family: "Consolas", "Fira Code", "SFMono-Regular", Menlo, monospace;
    font-size: .875em;
    background-color: #073642;
    border-radius: 4px;
    padding: .2em .4em;
    color: #dc322f;
}

pre {
    background-color: #073642;
    border: 1px solid #586e75;
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
    color: #839496;
}

blockquote {
    border-left: 4px solid #586e75;
    color: #586e75;
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
    border: 1px solid #586e75;
    padding: 6px 13px;
    text-align: left;
}
thead tr { background-color: #073642; font-weight: 600; }
tbody tr:nth-child(odd)  { background-color: #002b36; }
tbody tr:nth-child(even) { background-color: #073642; }

hr {
    height: 2px;
    background-color: #073642;
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
    border: 1.5px solid #586e75;
    border-radius: 3px;
    background-color: #002b36;
    position: relative;
    cursor: default;
}

li.task-item input[type="checkbox"]:checked {
    background-color: #268bd2;
    border-color: #268bd2;
}

li.task-item input[type="checkbox"]:checked::after {
    content: "";
    position: absolute;
    left: 4px;
    top: 1px;
    width: 4px;
    height: 8px;
    border: 2px solid #fdf6e3;
    border-top: none;
    border-left: none;
    transform: rotate(40deg);
}

li.task-item.done > span {
    color: #586e75;
    text-decoration: line-through;
    text-decoration-color: #586e75;
}

del {
    text-decoration: line-through;
    text-decoration-color: #586e75;
    color: #586e75;
}

.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #839496; }

.plantuml-diagram {
    text-align: center;
    margin: 20px 0;
}
.plantuml-diagram img {
    max-width: 100%;
    height: auto;
    background: transparent;
}

.footnote { font-size: .875em; color: #586e75; }
"""

_SOLARIZED_LIGHT_CSS = """
* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #657b83;
    background-color: #fdf6e3;
    padding: 24px 48px;
    max-width: 980px;
    margin: 0 auto;
}

h1, h2, h3, h4, h5, h6 {
    color: #586e75;
    font-weight: 600;
    line-height: 1.25;
    margin-top: 24px;
    margin-bottom: 16px;
    padding-bottom: .3em;
    border-bottom: 1px solid #eee8d5;
}
h1 { font-size: 2em; color: #268bd2; }
h2 { font-size: 1.5em; color: #2aa198; }
h3 { font-size: 1.25em; border-bottom: none; color: #859900; }
h4, h5, h6 { border-bottom: none; }

p { margin: 0 0 16px; }

a { color: #2aa198; text-decoration: none; }
a:hover { text-decoration: underline; }

code, kbd, samp {
    font-family: "Consolas", "Fira Code", "SFMono-Regular", Menlo, monospace;
    font-size: .875em;
    background-color: #eee8d5;
    border-radius: 4px;
    padding: .2em .4em;
    color: #dc322f;
}

pre {
    background-color: #eee8d5;
    border: 1px solid #93a1a1;
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
    color: #657b83;
}

blockquote {
    border-left: 4px solid #93a1a1;
    color: #93a1a1;
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
    border: 1px solid #93a1a1;
    padding: 6px 13px;
    text-align: left;
}
thead tr { background-color: #eee8d5; font-weight: 600; }
tbody tr:nth-child(odd)  { background-color: #fdf6e3; }
tbody tr:nth-child(even) { background-color: #eee8d5; }

hr {
    height: 2px;
    background-color: #eee8d5;
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
    border: 1.5px solid #93a1a1;
    border-radius: 3px;
    background-color: #fdf6e3;
    position: relative;
    cursor: default;
}

li.task-item input[type="checkbox"]:checked {
    background-color: #268bd2;
    border-color: #268bd2;
}

li.task-item input[type="checkbox"]:checked::after {
    content: "";
    position: absolute;
    left: 4px;
    top: 1px;
    width: 4px;
    height: 8px;
    border: 2px solid #fdf6e3;
    border-top: none;
    border-left: none;
    transform: rotate(40deg);
}

li.task-item.done > span {
    color: #93a1a1;
    text-decoration: line-through;
    text-decoration-color: #93a1a1;
}

del {
    text-decoration: line-through;
    text-decoration-color: #93a1a1;
    color: #93a1a1;
}

.math-block {
    overflow-x: auto;
    margin: 20px 0;
    text-align: center;
}
mjx-container { color: #657b83; }

.plantuml-diagram {
    text-align: center;
    margin: 20px 0;
}
.plantuml-diagram img {
    max-width: 100%;
    height: auto;
    background: transparent;
}

.footnote { font-size: .875em; color: #93a1a1; }
"""

# ── Preview Themes ────────────────────────────────────────────────────────────
# Tuple: (css_string, bg_hex)  — bg_hex is the WebEngine page background colour.

PREVIEW_THEMES: dict[str, tuple[str, str]] = {
    "GitHub Dark":     (_GITHUB_DARK_CSS,     "#0d1117"),
    "GitHub Light":    (_GITHUB_LIGHT_CSS,    "#ffffff"),
    "Solarized Dark":  (_SOLARIZED_DARK_CSS,  "#002b36"),
    "Solarized Light": (_SOLARIZED_LIGHT_CSS, "#fdf6e3"),
}

# ── App Themes ────────────────────────────────────────────────────────────────

APP_THEMES: list[str] = ["System", "Fusion Dark", "Fusion Light"]


def apply_app_theme(name: str, app) -> None:
    """Apply the selected application-wide theme.

    Must be called after QApplication is created but before any widgets
    are shown.  Requires a restart to take effect after a settings change.
    """
    from PyQt6.QtGui import QColor, QPalette
    from PyQt6.QtCore import Qt

    if name == "Fusion Dark":
        app.setStyle("Fusion")
        palette = QPalette()
        dark    = QColor(53,  53,  53)
        darker  = QColor(25,  25,  25)
        accent  = QColor(42, 130, 218)
        palette.setColor(QPalette.ColorRole.Window,          dark)
        palette.setColor(QPalette.ColorRole.WindowText,      Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base,            darker)
        palette.setColor(QPalette.ColorRole.AlternateBase,   dark)
        palette.setColor(QPalette.ColorRole.ToolTipBase,     Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.ToolTipText,     Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text,            Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button,          dark)
        palette.setColor(QPalette.ColorRole.ButtonText,      Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText,      Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link,            accent)
        palette.setColor(QPalette.ColorRole.Highlight,       accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        app.setPalette(palette)

    elif name == "Fusion Light":
        app.setStyle("Fusion")
        # Explicitly define a light palette so a dark system theme is not inherited.
        palette = QPalette()
        light  = QColor(240, 240, 240)
        white  = QColor(255, 255, 255)
        black  = QColor(0,   0,   0)
        accent = QColor(42, 130, 218)
        palette.setColor(QPalette.ColorRole.Window,          light)
        palette.setColor(QPalette.ColorRole.WindowText,      black)
        palette.setColor(QPalette.ColorRole.Base,            white)
        palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(233, 231, 227))
        palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(255, 255, 220))
        palette.setColor(QPalette.ColorRole.ToolTipText,     black)
        palette.setColor(QPalette.ColorRole.Text,            black)
        palette.setColor(QPalette.ColorRole.Button,          light)
        palette.setColor(QPalette.ColorRole.ButtonText,      black)
        palette.setColor(QPalette.ColorRole.BrightText,      Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link,            accent)
        palette.setColor(QPalette.ColorRole.Highlight,       accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, white)
        app.setPalette(palette)
