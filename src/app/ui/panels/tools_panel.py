from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ToolsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Tools Panel (placeholder)"))
        layout.addStretch(1)
