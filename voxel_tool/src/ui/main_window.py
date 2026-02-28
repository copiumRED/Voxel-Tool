"""Main Qt window shell with dockable panels and embedded viewport."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QLabel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Voxel Tool")
        self.setMinimumSize(1200, 800)
        self.setCentralWidget(QLabel("Viewport placeholder — wire ModernGL widget here."))
