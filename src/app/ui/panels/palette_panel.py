from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QGridLayout, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

from core.io.palette_io import load_palette_preset, save_palette_preset
from core.palette import clamp_active_color_index

if TYPE_CHECKING:
    from app.app_context import AppContext


class PalettePanel(QWidget):
    active_color_changed = Signal(int)
    palette_status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None
        self._buttons: list[QPushButton] = []

        root_layout = QVBoxLayout(self)
        grid = QGridLayout()
        root_layout.addLayout(grid)
        actions_row = QHBoxLayout()
        self.save_palette_button = QPushButton("Save Preset", self)
        self.save_palette_button.clicked.connect(self._on_save_palette)
        actions_row.addWidget(self.save_palette_button)
        self.load_palette_button = QPushButton("Load Preset", self)
        self.load_palette_button.clicked.connect(self._on_load_palette)
        actions_row.addWidget(self.load_palette_button)
        root_layout.addLayout(actions_row)
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

    def _on_save_palette(self) -> None:
        if self._context is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Palette Preset",
            "",
            "Palette Preset (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            save_palette_preset(self._context.palette, path)
            self.palette_status_message.emit(f"Saved palette preset: {path}")
        except Exception as exc:  # pragma: no cover
            QMessageBox.warning(self, "Save Palette Preset", f"Failed to save palette preset.\n\n{exc}")

    def _on_load_palette(self) -> None:
        if self._context is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Palette Preset",
            "",
            "Palette Preset (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            loaded_palette = load_palette_preset(path)
        except Exception as exc:  # pragma: no cover
            QMessageBox.warning(self, "Load Palette Preset", f"Failed to load palette preset.\n\n{exc}")
            return
        self._context.palette = loaded_palette
        self._context.active_color_index = clamp_active_color_index(
            self._context.active_color_index,
            len(loaded_palette),
        )
        self.refresh()
        self.active_color_changed.emit(self._context.active_color_index)
        self.palette_status_message.emit(f"Loaded palette preset: {path}")
