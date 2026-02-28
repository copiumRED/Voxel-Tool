from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PalettePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Palette Panel (placeholder)"))
        layout.addStretch(1)
