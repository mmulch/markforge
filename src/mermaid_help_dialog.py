"""Dialog that displays a comprehensive Mermaid reference."""

from __future__ import annotations

from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from i18n import current as _lang
from preview_widget import PreviewWidget

# ── Content ──────────────────────────────────────────────────────────────────

_CONTENT_EN = """\
# Mermaid Reference

Mermaid lets you create diagrams from plain text using JavaScript.
In this editor write a fenced code block with the language tag **`mermaid`**
and the diagram is rendered automatically in the preview
(mermaid.js is loaded from CDN on first use).

````
```mermaid
graph TD
    A[Start] --> B[End]
```
````

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -- Yes --> C[Done]
    B -- No  --> A
```

---

## Flowchart

Describes processes and decision flows.

**Node shapes**

| Syntax | Shape |
|---|---|
| `A[Text]` | Rectangle |
| `A(Text)` | Rounded rectangle |
| `A{Text}` | Diamond (decision) |
| `A((Text))` | Circle |
| `A>Text]` | Asymmetric |

**Arrow types**

| Syntax | Meaning |
|---|---|
| `A --> B` | Arrow |
| `A --- B` | Line |
| `A -- text --> B` | Arrow with label |
| `A -.-> B` | Dashed arrow |
| `A ==> B` | Thick arrow |

```mermaid
graph LR
    A([Start]) --> B[Process]
    B --> C{OK?}
    C -- Yes --> D([End])
    C -- No  --> E[Fix]
    E --> B
```

**Subgraphs**

```mermaid
graph TD
    subgraph Frontend
        A[Browser] --> B[API Call]
    end
    subgraph Backend
        C[Server] --> D[(Database)]
    end
    B --> C
```

---

## Sequence Diagram

Models the interaction between participants over time.

**Arrows**

| Syntax | Meaning |
|---|---|
| `A->>B: msg` | Solid arrow |
| `A-->>B: msg` | Dashed arrow (reply) |
| `A-xB: msg` | Cross head |
| `A-)B: msg` | Open head |

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant DB as Database
    C->>S: GET /data
    S->>DB: SELECT *
    DB-->>S: rows
    S-->>C: 200 OK
    note over S,DB: Internal call
```

**Loops and alternatives**

```mermaid
sequenceDiagram
    participant Client
    participant Server
    loop Retry up to 3 times
        Client->>Server: Request
        Server-->>Client: Response
    end
    alt success
        Server-->>Client: 200 OK
    else error
        Server-->>Client: 500 Error
    end
```

---

## Class Diagram

Shows classes, attributes, methods, and relationships.

**Visibility modifiers:** `+` public, `-` private, `#` protected, `~` package

**Relationships**

| Syntax | Meaning |
|---|---|
| `A <\\|-- B` | Inheritance |
| `A <\\|.. B` | Realization |
| `A *-- B` | Composition |
| `A o-- B` | Aggregation |
| `A --> B` | Association |
| `A ..> B` | Dependency |

```mermaid
classDiagram
    class Shape {
        <<abstract>>
        +color: String
        +area() float
    }
    class Circle {
        +radius: float
        +area() float
    }
    class Rectangle {
        +width: float
        +height: float
        +area() float
    }
    Shape <|-- Circle
    Shape <|-- Rectangle
```

---

## State Diagram

Represents states and transitions.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : submit
    Review --> Published : approve
    Review --> Draft : reject
    Published --> [*] : archive

    state Review {
        [*] --> Pending
        Pending --> Checked : check
        Checked --> [*]
    }
```

---

## Gantt Chart

Visualizes project schedules.

```mermaid
gantt
    title Software Release
    dateFormat  YYYY-MM-DD
    excludes    weekends
    section Design
    Wireframes     :done,    d1, 2024-01-01, 5d
    Mockups        :active,  d2, after d1,  5d
    section Development
    Backend        :         dev1, after d2, 15d
    Frontend       :         dev2, after d2, 12d
    section Launch
    Testing        :crit,    t1, after dev1, 7d
    Release        :milestone, after t1, 0d
```

---

## Pie Chart

```mermaid
pie showData title Sales by Region
    "North" : 42
    "South" : 28
    "East"  : 18
    "West"  : 12
```

---

## Mind Map

```mermaid
mindmap
    root((MarkForge))
        Editor
            Syntax highlighting
            Line numbers
            Themes
        Preview
            Live rendering
            Math via MathJax
            Diagrams
        Git
            Clone
            Commit & Push
            Squash
```

---

## ER Diagram

Entity-Relationship diagrams for databases.

**Cardinality**

| Syntax | Meaning |
|---|---|
| `\\|\\|` | Exactly one |
| `o\\|` | Zero or one |
| `\\|\\{` | One or more |
| `o\\{` | Zero or more |

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
    }
    POST {
        int id PK
        string title
        text content
        int user_id FK
    }
    COMMENT {
        int id PK
        text body
        int post_id FK
    }
    USER ||--o{ POST : writes
    POST ||--o{ COMMENT : has
```

---

## Git Graph

Visualizes git branch history.

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feature A"
    commit id: "feature B"
    checkout main
    merge develop id: "merge"
    commit id: "hotfix"
    branch release
    checkout release
    commit id: "v1.0"
```

---

## Tips

- Diagrams are rendered by **mermaid.js** directly in the browser — no server needed.
- Mermaid.js is loaded from CDN on first use and cached by the browser.
- Full reference: [mermaid.js.org](https://mermaid.js.org/)
"""

_CONTENT_DE = """\
# Mermaid-Referenz

Mermaid ermöglicht es, Diagramme aus Klartext mit JavaScript zu erstellen.
Schreiben Sie in diesem Editor einen eingezäunten Codeblock mit dem
Sprach-Tag **`mermaid`** – das Diagramm wird automatisch in der Vorschau
gerendert (mermaid.js wird beim ersten Einsatz vom CDN geladen).

````
```mermaid
graph TD
    A[Start] --> B[Ende]
```
````

```mermaid
graph TD
    A[Start] --> B{Entscheidung}
    B -- Ja  --> C[Fertig]
    B -- Nein --> A
```

---

## Flussdiagramm

Beschreibt Prozesse und Entscheidungsabläufe.

**Knotenformen**

| Syntax | Form |
|---|---|
| `A[Text]` | Rechteck |
| `A(Text)` | Abgerundetes Rechteck |
| `A{Text}` | Raute (Entscheidung) |
| `A((Text))` | Kreis |
| `A>Text]` | Asymmetrisch |

**Pfeiltypen**

| Syntax | Bedeutung |
|---|---|
| `A --> B` | Pfeil |
| `A --- B` | Linie |
| `A -- Text --> B` | Pfeil mit Beschriftung |
| `A -.-> B` | Gestrichelter Pfeil |
| `A ==> B` | Dicker Pfeil |

```mermaid
graph LR
    A([Start]) --> B[Verarbeitung]
    B --> C{OK?}
    C -- Ja   --> D([Ende])
    C -- Nein --> E[Korrektur]
    E --> B
```

**Teilgraphen**

```mermaid
graph TD
    subgraph Frontend
        A[Browser] --> B[API-Aufruf]
    end
    subgraph Backend
        C[Server] --> D[(Datenbank)]
    end
    B --> C
```

---

## Sequenzdiagramm

Modelliert die Interaktion zwischen Teilnehmern über die Zeit.

**Pfeile**

| Syntax | Bedeutung |
|---|---|
| `A->>B: Nachricht` | Ausgefüllter Pfeil |
| `A-->>B: Nachricht` | Gestrichelter Pfeil (Antwort) |
| `A-xB: Nachricht` | Kreuzpfeil |
| `A-)B: Nachricht` | Offener Pfeil |

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant DB as Datenbank
    C->>S: GET /daten
    S->>DB: SELECT *
    DB-->>S: Zeilen
    S-->>C: 200 OK
    note over S,DB: Interner Aufruf
```

**Schleifen und Alternativen**

```mermaid
sequenceDiagram
    participant Client
    participant Server
    loop Bis zu 3 Versuche
        Client->>Server: Anfrage
        Server-->>Client: Antwort
    end
    alt Erfolg
        Server-->>Client: 200 OK
    else Fehler
        Server-->>Client: 500 Error
    end
```

---

## Klassendiagramm

Zeigt Klassen, Attribute, Methoden und Beziehungen.

**Sichtbarkeit:** `+` öffentlich, `-` privat, `#` geschützt, `~` Paket

**Beziehungen**

| Syntax | Bedeutung |
|---|---|
| `A <\\|-- B` | Vererbung |
| `A <\\|.. B` | Realisierung |
| `A *-- B` | Komposition |
| `A o-- B` | Aggregation |
| `A --> B` | Assoziation |
| `A ..> B` | Abhängigkeit |

```mermaid
classDiagram
    class Form {
        <<abstract>>
        +farbe: String
        +flaeche() float
    }
    class Kreis {
        +radius: float
        +flaeche() float
    }
    class Rechteck {
        +breite: float
        +hoehe: float
        +flaeche() float
    }
    Form <|-- Kreis
    Form <|-- Rechteck
```

---

## Zustandsdiagramm

Stellt Zustände und Übergänge dar.

```mermaid
stateDiagram-v2
    [*] --> Entwurf
    Entwurf --> Überprüfung : einreichen
    Überprüfung --> Veröffentlicht : genehmigen
    Überprüfung --> Entwurf : ablehnen
    Veröffentlicht --> [*] : archivieren

    state Überprüfung {
        [*] --> Ausstehend
        Ausstehend --> Geprüft : prüfen
        Geprüft --> [*]
    }
```

---

## Gantt-Diagramm

Visualisiert Projektzeitpläne.

```mermaid
gantt
    title Software-Release
    dateFormat  YYYY-MM-DD
    excludes    weekends
    section Design
    Wireframes     :done,    d1, 2024-01-01, 5d
    Mockups        :active,  d2, after d1,  5d
    section Entwicklung
    Backend        :         dev1, after d2, 15d
    Frontend       :         dev2, after d2, 12d
    section Launch
    Tests          :crit,    t1, after dev1, 7d
    Release        :milestone, after t1, 0d
```

---

## Tortendiagramm

```mermaid
pie showData title Umsatz nach Region
    "Nord" : 42
    "Süd"  : 28
    "Ost"  : 18
    "West" : 12
```

---

## MindMap

```mermaid
mindmap
    root((MarkForge))
        Editor
            Syntaxhervorhebung
            Zeilennummern
            Themes
        Vorschau
            Live-Rendering
            Mathematik via MathJax
            Diagramme
        Git
            Klonen
            Commit & Push
            Squash
```

---

## ER-Diagramm

Entity-Relationship-Diagramme für Datenbanken.

**Kardinalität**

| Syntax | Bedeutung |
|---|---|
| `\\|\\|` | Genau eins |
| `o\\|` | Null oder eins |
| `\\|\\{` | Eins oder mehr |
| `o\\{` | Null oder mehr |

```mermaid
erDiagram
    BENUTZER {
        int id PK
        string benutzername
        string email
    }
    BEITRAG {
        int id PK
        string titel
        text inhalt
        int benutzer_id FK
    }
    KOMMENTAR {
        int id PK
        text text
        int beitrag_id FK
    }
    BENUTZER ||--o{ BEITRAG : schreibt
    BEITRAG ||--o{ KOMMENTAR : hat
```

---

## Git-Graph

Visualisiert Git-Branch-Verläufe.

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "Feature A"
    commit id: "Feature B"
    checkout main
    merge develop id: "Merge"
    commit id: "Hotfix"
    branch release
    checkout release
    commit id: "v1.0"
```

---

## Tipps

- Diagramme werden von **mermaid.js** direkt im Browser gerendert – kein Server nötig.
- mermaid.js wird beim ersten Einsatz vom CDN geladen und vom Browser gecacht.
- Vollständige Referenz: [mermaid.js.org](https://mermaid.js.org/)
"""


class MermaidHelpDialog(QDialog):
    """Non-modal dialog showing a Mermaid syntax reference."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            "Mermaid-Referenz" if _lang() == "de" else "Mermaid Reference"
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
