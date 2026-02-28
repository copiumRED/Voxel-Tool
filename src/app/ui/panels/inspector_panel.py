from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class InspectorPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Inspector Panel (placeholder)"))
        layout.addStretch(1)
