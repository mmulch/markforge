"""Dialog for creating and inserting PlantUML diagrams."""

from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)

# ── Diagramm-Vorlagen ─────────────────────────────────────────────────────────

_TEMPLATES: dict[str, str] = {
    "Sequenzdiagramm": """\
@startuml
Alice -> Bob: Anfrage
Bob --> Alice: Antwort
note right of Bob: Verarbeitung
@enduml""",

    "Klassendiagramm": """\
@startuml
class Fahrzeug {
  - marke: String
  - baujahr: int
  + fahren(): void
}
class Auto {
  - tueren: int
  + hupen(): void
}
Fahrzeug <|-- Auto
@enduml""",

    "Aktivitätsdiagramm": """\
@startuml
start
:Schritt 1;
if (Bedingung?) then (ja)
  :Schritt 2a;
else (nein)
  :Schritt 2b;
endif
:Schritt 3;
stop
@enduml""",

    "Zustandsdiagramm": """\
@startuml
[*] --> Leerlauf
Leerlauf --> Aktiv : start
Aktiv --> Leerlauf : stop
Aktiv --> Fehler : error
Fehler --> [*]
@enduml""",

    "Komponentendiagramm": """\
@startuml
package "Frontend" {
  component Browser
}
package "Backend" {
  component Server
  component Datenbank
}
Browser --> Server : HTTP
Server --> Datenbank : SQL
@enduml""",

    "Anwendungsfalldiagramm": """\
@startuml
left to right direction
actor Benutzer
actor Admin
rectangle System {
  usecase "Anmelden" as UC1
  usecase "Daten ansehen" as UC2
  usecase "Daten bearbeiten" as UC3
}
Benutzer --> UC1
Benutzer --> UC2
Admin --> UC3
@enduml""",

    "Gantt-Diagramm": """\
@startgantt
[Aufgabe 1] lasts 5 days
[Aufgabe 2] lasts 3 days
[Aufgabe 2] starts at [Aufgabe 1]'s end
[Aufgabe 3] lasts 4 days
[Aufgabe 3] starts at [Aufgabe 2]'s end
@endgantt""",

    "MindMap": """\
@startmindmap
* Hauptthema
** Thema 1
*** Detail 1.1
*** Detail 1.2
** Thema 2
*** Detail 2.1
@endmindmap""",

    "WBS (Arbeitsstruktur)": """\
@startwbs
* Projekt
** Phase 1
*** Aufgabe 1.1
*** Aufgabe 1.2
** Phase 2
*** Aufgabe 2.1
@endwbs""",

    "Timing-Diagramm": """\
@startuml
concise "Signal A" as A
concise "Signal B" as B
@0
A is inaktiv
B is inaktiv
@2
A is aktiv
@4
B is aktiv
@6
A is inaktiv
B is inaktiv
@enduml""",

    "Deployment-Diagramm": """\
@startuml
node "Webserver" {
  artifact "app.war"
}
node "Datenbankserver" {
  database "MySQL"
}
"Webserver" --> "Datenbankserver" : JDBC
@enduml""",

    "JSON": """\
@startjson
{
  "name": "Beispiel",
  "wert": 42,
  "liste": [1, 2, 3],
  "verschachtelt": {
    "aktiv": true
  }
}
@endjson""",
}


class InsertPlantUMLDialog(QDialog):
    """Creates a PlantUML diagram and inserts it as a fenced code block."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PlantUML-Diagramm einfügen")
        self.setMinimumSize(620, 480)
        self._build_ui()
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._on_type_changed(0)

    # ── UI-Aufbau ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # Diagrammtyp-Zeile
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Diagrammtyp:"))
        self._type_combo = QComboBox()
        self._type_combo.addItems(list(_TEMPLATES.keys()))
        type_row.addWidget(self._type_combo, 1)
        root.addLayout(type_row)

        # Code-Editor
        root.addWidget(QLabel("PlantUML-Code:"))
        self._editor = QPlainTextEdit()
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(font)
        self._editor.setTabStopDistance(28.0)
        root.addWidget(self._editor, 1)

        # Hinweis
        hint = QLabel(
            "Tipp: Die Vorschau des Diagramms erscheint nach dem Einfügen"
            " automatisch im Hauptfenster (Internetverbindung erforderlich)."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6e7681; font-size: 12px;")
        root.addWidget(hint)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_type_changed(self, index: int) -> None:
        name = self._type_combo.currentText()
        self._editor.setPlainText(_TEMPLATES.get(name, ""))

    # ── Public API ────────────────────────────────────────────────────────────

    def get_markdown(self) -> str:
        """Returns the PlantUML code as a Markdown fenced block."""
        code = self._editor.toPlainText().strip()
        if not code:
            return ""
        return f"```plantuml\n{code}\n```"
