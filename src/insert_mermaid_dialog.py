"""Dialog for creating and inserting Mermaid diagrams."""

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

from i18n import tr

# ── Diagram templates (keys are English; tr() is used for display) ────────────

_TEMPLATES: dict[str, str] = {
    "Flowchart": """\
graph TD
    A[Start] --> B{Decision}
    B -- Yes --> C[Action 1]
    B -- No  --> D[Action 2]
    C --> E[End]
    D --> E""",

    "Sequence diagram": """\
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob!
    Bob-->>Alice: Hi Alice!
    Alice->>Bob: How are you?
    Bob-->>Alice: Fine, thanks!""",

    "Class diagram": """\
classDiagram
    class Animal {
        +String name
        +int age
        +speak() void
    }
    class Dog {
        +String breed
        +fetch() void
    }
    Animal <|-- Dog""",

    "State diagram": """\
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start
    Running --> Paused : pause
    Paused --> Running : resume
    Running --> [*] : stop""",

    "Gantt": """\
gantt
    title Project Plan
    dateFormat  YYYY-MM-DD
    section Phase 1
    Design        :a1, 2024-01-01, 10d
    section Phase 2
    Development   :a2, after a1, 20d
    section Phase 3
    Testing       :a3, after a2, 10d""",

    "Pie chart": """\
pie title Browser Usage
    "Chrome"  : 65
    "Firefox" : 15
    "Safari"  : 12
    "Other"   : 8""",

    "Mind map": """\
mindmap
    root((Project))
        Planning
            Requirements
            Timeline
        Development
            Frontend
            Backend
        Testing""",

    "ER diagram": """\
erDiagram
    CUSTOMER {
        int id
        string name
        string email
    }
    ORDER {
        int id
        date created
        float total
    }
    CUSTOMER ||--o{ ORDER : places""",

    "Git graph": """\
gitGraph
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit""",
}


class InsertMermaidDialog(QDialog):
    """Creates a Mermaid diagram and inserts it as a fenced code block."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("Insert Mermaid Diagram"))
        self.setMinimumSize(620, 480)
        self._build_ui()
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
        self._on_type_changed(0)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel(tr("Diagram type:")))
        self._type_combo = QComboBox()
        for key in _TEMPLATES:
            self._type_combo.addItem(tr(key), key)
        type_row.addWidget(self._type_combo, 1)
        root.addLayout(type_row)

        root.addWidget(QLabel(tr("Mermaid code:")))
        self._editor = QPlainTextEdit()
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(font)
        self._editor.setTabStopDistance(28.0)
        root.addWidget(self._editor, 1)

        hint = QLabel(
            tr(
                "Tip: The diagram preview appears automatically in the main window after inserting"
                " (mermaid.js is loaded from CDN on first use)."
            )
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6e7681; font-size: 12px;")
        root.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_type_changed(self, index: int) -> None:
        key = self._type_combo.currentData()
        self._editor.setPlainText(_TEMPLATES.get(key, ""))

    # ── Public API ────────────────────────────────────────────────────────────

    def get_markdown(self) -> str:
        """Returns the Mermaid code as a Markdown fenced block."""
        code = self._editor.toPlainText().strip()
        if not code:
            return ""
        return f"```mermaid\n{code}\n```"
