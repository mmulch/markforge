"""Dialog that displays a comprehensive Markdown reference."""

from __future__ import annotations

from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from i18n import current as _lang
from preview_widget import PreviewWidget

# ── Content ──────────────────────────────────────────────────────────────────

_CONTENT_EN = """\
# Markdown Reference

Markdown is a lightweight markup language that lets you format plain text using
simple punctuation. The formatted output is usually converted to HTML.

---

## Headings

Use `#` signs (1–6) at the start of a line. More signs = smaller heading.

```
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

---

## Emphasis

| Syntax | Result |
|---|---|
| `**bold**` or `__bold__` | **bold** |
| `*italic*` or `_italic_` | *italic* |
| `***bold and italic***` | ***bold and italic*** |
| `~~strikethrough~~` | ~~strikethrough~~ |

---

## Blockquotes

Start lines with `>`. Nest with `>>`.

```
> This is a blockquote.
>
> It can span multiple paragraphs.
>
>> Nested blockquote.
```

> This is a blockquote.
>
>> Nested blockquote.

---

## Lists

**Unordered** – use `-`, `*`, or `+`:

```
- First item
- Second item
  - Nested item
```

- First item
- Second item
  - Nested item

**Ordered** – use numbers followed by `.`:

```
1. First
2. Second
3. Third
```

1. First
2. Second
3. Third

**Task list** – use `[ ]` and `[x]`:

```
- [ ] Open task
- [x] Completed task
```

- [ ] Open task
- [x] Completed task

---

## Code

**Inline code** – wrap in backticks:

```
Use the `print()` function.
```

Use the `print()` function.

**Code block** – wrap in triple backticks, optionally with a language name:

````
```python
def greet(name):
    return f"Hello, {name}!"
```
````

```python
def greet(name):
    return f"Hello, {name}!"
```

---

## Horizontal Rule

Three or more `---`, `***`, or `___` on their own line:

```
---
```

---

## Links

```
[Link text](https://example.com)
[Link with tooltip](https://example.com "Tooltip text")
```

[Link text](https://example.com)

---

## Images

```
![Alt text](https://via.placeholder.com/120x40 "Optional title")
```

---

## Tables

Use `|` to separate columns and `-` for the header row.
Colons control alignment.

```
| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
| D    |   E    |     F |
```

| Left | Center | Right |
|:-----|:------:|------:|
| A    |   B    |     C |
| D    |   E    |     F |

---

## Escaping Characters

Use a backslash `\\` before a special character to display it literally:

```
\\*not italic\\*   \\_not italic\\_   \\# not a heading
```

\\*not italic\\*   \\_not italic\\_   \\# not a heading

---

## Supported Extensions in this Editor

| Extension | Description |
|---|---|
| **Extra** | Tables, footnotes, abbreviations, attribute lists |
| **Fenced Code Blocks** | ` ```lang … ``` ` with syntax highlighting |
| **Table of Contents** | `[TOC]` inserts an automatic table of contents |
| **Task Lists** | `[ ]` / `[x]` checkboxes |
| **Math** | `$inline$` and `$$block$$` via MathJax |
| **PlantUML** | ` ```plantuml … ``` ` renders diagrams |
| **Strikethrough** | `~~text~~` |
| **Autolinks** | Bare URLs are linked automatically |

---

*More information: [markdownguide.org](https://www.markdownguide.org)*
"""

_CONTENT_DE = """\
# Markdown-Referenz

Markdown ist eine leichtgewichtige Auszeichnungssprache, mit der Sie
Klartext mithilfe einfacher Satzzeichen formatieren können.
Die Ausgabe wird üblicherweise in HTML umgewandelt.

---

## Überschriften

Verwenden Sie `#`-Zeichen (1–6) am Zeilenanfang. Mehr Zeichen = kleinere Überschrift.

```
# Überschrift 1
## Überschrift 2
### Überschrift 3
#### Überschrift 4
##### Überschrift 5
###### Überschrift 6
```

---

## Hervorhebungen

| Syntax | Ergebnis |
|---|---|
| `**fett**` oder `__fett__` | **fett** |
| `*kursiv*` oder `_kursiv_` | *kursiv* |
| `***fett und kursiv***` | ***fett und kursiv*** |
| `~~durchgestrichen~~` | ~~durchgestrichen~~ |

---

## Zitate (Blockquotes)

Zeilen mit `>` beginnen. Mit `>>` verschachteln.

```
> Dies ist ein Zitat.
>
> Es kann mehrere Absätze umfassen.
>
>> Verschachteltes Zitat.
```

> Dies ist ein Zitat.
>
>> Verschachteltes Zitat.

---

## Listen

**Ungeordnet** – mit `-`, `*` oder `+`:

```
- Erster Punkt
- Zweiter Punkt
  - Unterpunkt
```

- Erster Punkt
- Zweiter Punkt
  - Unterpunkt

**Geordnet** – mit Zahlen gefolgt von `.`:

```
1. Erster
2. Zweiter
3. Dritter
```

1. Erster
2. Zweiter
3. Dritter

**Aufgabenliste** – mit `[ ]` und `[x]`:

```
- [ ] Offene Aufgabe
- [x] Erledigte Aufgabe
```

- [ ] Offene Aufgabe
- [x] Erledigte Aufgabe

---

## Code

**Inline-Code** – in Backticks einschließen:

```
Verwenden Sie die Funktion `print()`.
```

Verwenden Sie die Funktion `print()`.

**Codeblock** – in dreifache Backticks einschließen, optional mit Sprachname:

````
```python
def begruesse(name):
    return f"Hallo, {name}!"
```
````

```python
def begruesse(name):
    return f"Hallo, {name}!"
```

---

## Horizontale Linie

Drei oder mehr `---`, `***` oder `___` auf einer eigenen Zeile:

```
---
```

---

## Links

```
[Linktext](https://beispiel.de)
[Link mit Tooltip](https://beispiel.de "Tooltip-Text")
```

[Linktext](https://example.com)

---

## Bilder

```
![Alternativtext](https://via.placeholder.com/120x40 "Optionaler Titel")
```

---

## Tabellen

`|` trennt Spalten, `-` bildet die Kopfzeile.
Doppelpunkte steuern die Ausrichtung.

```
| Links | Zentriert | Rechts |
|:------|:---------:|-------:|
| A     |     B     |      C |
| D     |     E     |      F |
```

| Links | Zentriert | Rechts |
|:------|:---------:|-------:|
| A     |     B     |      C |
| D     |     E     |      F |

---

## Sonderzeichen maskieren

Mit einem Backslash `\\` vor einem Sonderzeichen wird dieser literal angezeigt:

```
\\*kein Kursiv\\*   \\_kein Kursiv\\_   \\# keine Überschrift
```

\\*kein Kursiv\\*   \\_kein Kursiv\\_   \\# keine Überschrift

---

## Unterstützte Erweiterungen in diesem Editor

| Erweiterung | Beschreibung |
|---|---|
| **Extra** | Tabellen, Fußnoten, Abkürzungen, Attributlisten |
| **Fenced Code Blocks** | ` ```Sprache … ``` ` mit Syntaxhervorhebung |
| **Inhaltsverzeichnis** | `[TOC]` fügt ein automatisches Inhaltsverzeichnis ein |
| **Aufgabenlisten** | `[ ]` / `[x]` Kontrollkästchen |
| **Mathematik** | `$inline$` und `$$block$$` via MathJax |
| **PlantUML** | ` ```plantuml … ``` ` rendert Diagramme |
| **Durchgestrichen** | `~~Text~~` |
| **Autolinks** | Bare URLs werden automatisch verlinkt |

---

*Weitere Informationen: [markdownguide.org](https://www.markdownguide.org)*
"""


class MarkdownHelpDialog(QDialog):
    """Non-modal dialog showing a Markdown syntax reference."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            "Markdown-Referenz" if _lang() == "de" else "Markdown Reference"
        )
        self.resize(QSize(820, 680))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)

        self._preview = PreviewWidget()
        layout.addWidget(self._preview)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)

        content = _CONTENT_DE if _lang() == "de" else _CONTENT_EN
        self._preview.set_markdown(content, QUrl())
