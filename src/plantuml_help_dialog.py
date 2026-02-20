"""Dialog that displays a comprehensive PlantUML reference."""

from __future__ import annotations

from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from i18n import current as _lang
from preview_widget import PreviewWidget

# ── Content ──────────────────────────────────────────────────────────────────

_CONTENT_EN = """\
# PlantUML Reference

PlantUML lets you create diagrams from plain text.
In this editor write a fenced code block with the language tag **`plantuml`**
and the diagram is rendered automatically in the preview
(an internet connection to the PlantUML server is required).

````
```plantuml
Alice -> Bob: Hello!
Bob --> Alice: Hi!
```
````

```plantuml
Alice -> Bob: Hello!
Bob --> Alice: Hi!
```

---

## Sequence Diagram

Models the interaction between participants over time.

**Participants**

```
participant Alice
actor       Bob
boundary    System
database    DB
```

**Arrows**

| Syntax | Meaning |
|---|---|
| `A -> B: msg` | Solid arrow |
| `A --> B: msg` | Dashed arrow (reply) |
| `A ->> B: msg` | Open arrowhead |
| `A ->x B: msg` | Lost message |
| `A ->o B: msg` | Circle arrowhead |

**Activation, notes, groups**

```plantuml
participant Alice
participant Bob
autonumber
Alice -> Bob: Request
activate Bob
note right: Processing
Bob --> Alice: Response
deactivate Bob
group Error handling
  Alice -> Bob: Retry
end
```

**Loops and alternatives**

```plantuml
participant Client
participant Server
loop 3 times
  Client -> Server: Ping
  Server --> Client: Pong
end
alt success
  Server --> Client: 200 OK
else failure
  Server --> Client: 500 Error
end
```

---

## Class Diagram

Shows classes, their attributes, methods, and relationships.

**Classes and members**

```
class Animal {
  +name: String
  #age: int
  +speak(): void
  {abstract} move(): void
}
```

**Relations**

| Syntax | Meaning |
|---|---|
| `A <\\|-- B` | Inheritance (B extends A) |
| `A <\\|.. B` | Realization (B implements A) |
| `A *-- B` | Composition |
| `A o-- B` | Aggregation |
| `A --> B` | Association |
| `A ..> B` | Dependency |

```plantuml
abstract class Animal {
  +name: String
  +speak(): void
}
class Dog {
  +breed: String
  +fetch(): void
}
interface Trainable {
  +train(): void
}
Animal <|-- Dog
Dog ..|> Trainable
```

---

## Activity Diagram

Describes workflows and business processes.

**Structure**

```
start
:Action;
if (condition?) then (yes)
  :Branch A;
else (no)
  :Branch B;
endif
stop
```

**Loops and swimlanes**

```plantuml
|User|
start
:Enter data;
|System|
repeat
  :Validate;
repeat while (invalid?) is (yes)
:Save;
|User|
:Confirm;
stop
```

**Fork (parallel)**

```plantuml
start
fork
  :Task A;
fork again
  :Task B;
end fork
:Merge;
stop
```

---

## Use Case Diagram

Shows actors and the system functions they use.

```plantuml
left to right direction
actor Customer
actor Admin

package "Online Shop" {
  (Browse products)
  (Place order)
  (Manage inventory)
}

Customer --> (Browse products)
Customer --> (Place order)
Admin    --> (Manage inventory)
Admin    --> (Place order)
```

---

## State Diagram

Represents the states of an object and transitions between them.

```plantuml
[*] --> Idle

Idle --> Running  : start
Running --> Paused : pause
Paused  --> Running : resume
Running --> [*]   : stop

state Running {
  [*] --> Processing
  Processing --> Waiting
  Waiting --> Processing
}
```

---

## Gantt Chart

```plantuml
Project starts 2024-01-01
[Design]     lasts 10 days
[Development] lasts 20 days
[Development] starts at [Design]'s end
[Testing]    lasts 10 days
[Testing]    starts at [Development]'s end
```

---

## Mind Map

```plantuml
@startmindmap
* Project
** Planning
*** Requirements
*** Timeline
** Development
*** Frontend
*** Backend
** Testing
@endmindmap
```

---

## Tips

- The `@startuml` / `@enduml` delimiters are **optional** in this editor –
  the fence block handles them automatically.
- Diagrams are rendered by the public PlantUML server and require an
  **internet connection**.
- Use `skinparam` to style diagrams, e.g. `skinparam monochrome true`.
- Full reference: [plantuml.com](https://plantuml.com/en/)
"""

_CONTENT_DE = """\
# PlantUML-Referenz

PlantUML ermöglicht es, Diagramme aus Klartext zu erstellen.
Schreiben Sie in diesem Editor einen eingezäunten Codeblock mit dem
Sprach-Tag **`plantuml`** – das Diagramm wird automatisch in der Vorschau
gerendert (eine Internetverbindung zum PlantUML-Server ist erforderlich).

````
```plantuml
Alice -> Bob: Hallo!
Bob --> Alice: Hi!
```
````

```plantuml
Alice -> Bob: Hallo!
Bob --> Alice: Hi!
```

---

## Sequenzdiagramm

Modelliert die Interaktion zwischen Teilnehmern über die Zeit.

**Teilnehmer**

```
participant Alice
actor       Bob
boundary    System
database    DB
```

**Pfeile**

| Syntax | Bedeutung |
|---|---|
| `A -> B: Nachricht` | Ausgefüllter Pfeil |
| `A --> B: Nachricht` | Gestrichelter Pfeil (Antwort) |
| `A ->> B: Nachricht` | Offener Pfeilkopf |
| `A ->x B: Nachricht` | Verlorene Nachricht |
| `A ->o B: Nachricht` | Kreis-Pfeilkopf |

**Aktivierung, Notizen, Gruppen**

```plantuml
participant Alice
participant Bob
autonumber
Alice -> Bob: Anfrage
activate Bob
note right: Verarbeitung
Bob --> Alice: Antwort
deactivate Bob
group Fehlerbehandlung
  Alice -> Bob: Erneuter Versuch
end
```

**Schleifen und Alternativen**

```plantuml
participant Client
participant Server
loop 3 Mal
  Client -> Server: Ping
  Server --> Client: Pong
end
alt Erfolg
  Server --> Client: 200 OK
else Fehler
  Server --> Client: 500 Error
end
```

---

## Klassendiagramm

Zeigt Klassen, Attribute, Methoden und Beziehungen.

**Klassen und Member**

```
class Tier {
  +name: String
  #alter: int
  +sprechen(): void
  {abstract} bewegen(): void
}
```

**Beziehungen**

| Syntax | Bedeutung |
|---|---|
| `A <\\|-- B` | Vererbung (B erbt von A) |
| `A <\\|.. B` | Realisierung (B implementiert A) |
| `A *-- B` | Komposition |
| `A o-- B` | Aggregation |
| `A --> B` | Assoziation |
| `A ..> B` | Abhängigkeit |

```plantuml
abstract class Tier {
  +name: String
  +sprechen(): void
}
class Hund {
  +rasse: String
  +apportieren(): void
}
interface Trainierbar {
  +trainieren(): void
}
Tier <|-- Hund
Hund ..|> Trainierbar
```

---

## Aktivitätsdiagramm

Beschreibt Arbeitsabläufe und Geschäftsprozesse.

**Struktur**

```
start
:Aktion;
if (Bedingung?) then (ja)
  :Zweig A;
else (nein)
  :Zweig B;
endif
stop
```

**Schleifen und Swimlanes**

```plantuml
|Benutzer|
start
:Daten eingeben;
|System|
repeat
  :Validieren;
repeat while (ungültig?) is (ja)
:Speichern;
|Benutzer|
:Bestätigen;
stop
```

**Fork (parallel)**

```plantuml
start
fork
  :Aufgabe A;
fork again
  :Aufgabe B;
end fork
:Zusammenführen;
stop
```

---

## Anwendungsfalldiagramm

Zeigt Akteure und die Systemfunktionen, die sie nutzen.

```plantuml
left to right direction
actor Kunde
actor Admin

package "Online-Shop" {
  (Produkte ansehen)
  (Bestellung aufgeben)
  (Lager verwalten)
}

Kunde --> (Produkte ansehen)
Kunde --> (Bestellung aufgeben)
Admin --> (Lager verwalten)
Admin --> (Bestellung aufgeben)
```

---

## Zustandsdiagramm

Stellt Zustände eines Objekts und Übergänge zwischen ihnen dar.

```plantuml
[*] --> Leerlauf

Leerlauf  --> Laufend  : starten
Laufend   --> Pausiert : pausieren
Pausiert  --> Laufend  : fortsetzen
Laufend   --> [*]      : stoppen

state Laufend {
  [*] --> Verarbeitung
  Verarbeitung --> Wartend
  Wartend --> Verarbeitung
}
```

---

## Gantt-Diagramm

```plantuml
Project starts 2024-01-01
[Design]       lasts 10 days
[Entwicklung]  lasts 20 days
[Entwicklung]  starts at [Design]'s end
[Test]         lasts 10 days
[Test]         starts at [Entwicklung]'s end
```

---

## MindMap

```plantuml
@startmindmap
* Projekt
** Planung
*** Anforderungen
*** Zeitplan
** Entwicklung
*** Frontend
*** Backend
** Test
@endmindmap
```

---

## Tipps

- Die Marker `@startuml` / `@enduml` sind in diesem Editor **optional** –
  der Fenced-Block übernimmt das automatisch.
- Diagramme werden vom öffentlichen PlantUML-Server gerendert und benötigen
  eine **Internetverbindung**.
- Mit `skinparam` lassen sich Diagramme gestalten, z. B.
  `skinparam monochrome true`.
- Vollständige Referenz: [plantuml.com](https://plantuml.com/en/)
"""


class PlantUMLHelpDialog(QDialog):
    """Non-modal dialog showing a PlantUML syntax reference."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(
            "PlantUML-Referenz" if _lang() == "de" else "PlantUML Reference"
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
