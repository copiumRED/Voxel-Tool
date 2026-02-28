from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from app.app_context import AppContext


class PalettePanel(QWidget):
    active_color_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None
        self._buttons: list[QPushButton] = []

        root_layout = QVBoxLayout(self)
        grid = QGridLayout()
        root_layout.addLayout(grid)
        root_layout.addStretch(1)

        for idx in range(8):
            button = QPushButton("")
            button.setFixedSize(28, 28)
            button.clicked.connect(lambda _checked=False, i=idx: self._on_color_clicked(i))
            row = idx // 4
            col = idx % 4
            grid.addWidget(button, row, col)
            self._buttons.append(button)

    def set_context(self, ctx: "AppContext") -> None:
        self._context = ctx
        self.refresh()

    def refresh(self) -> None:
        if self._context is None:
            return
        for idx, button in enumerate(self._buttons):
            rgb = self._context.palette[idx]
            selected = idx == self._context.active_color_index
            border = "2px solid #ffffff" if selected else "1px solid #444444"
            button.setStyleSheet(
                f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: {border};"
            )

    def _on_color_clicked(self, idx: int) -> None:
        if self._context is None:
            return
        self._context.active_color_index = idx
        self.refresh()
        self.active_color_changed.emit(idx)
