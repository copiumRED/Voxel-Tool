from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.io.palette_io import load_palette_preset, save_palette_preset
from core.palette import add_palette_color, clamp_active_color_index, remove_palette_color, swap_palette_colors

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
        self.grid = QGridLayout()
        root_layout.addLayout(self.grid)

        rgb_row = QHBoxLayout()
        self.r_spin = QSpinBox(self)
        self.g_spin = QSpinBox(self)
        self.b_spin = QSpinBox(self)
        for spin, label in ((self.r_spin, "R"), (self.g_spin, "G"), (self.b_spin, "B")):
            spin.setRange(0, 255)
            spin.valueChanged.connect(self._on_rgb_changed)
            rgb_row.addWidget(QLabel(label, self))
            rgb_row.addWidget(spin)
        root_layout.addLayout(rgb_row)

        edit_row = QHBoxLayout()
        self.add_color_button = QPushButton("Add", self)
        self.add_color_button.clicked.connect(self._on_add_color)
        edit_row.addWidget(self.add_color_button)
        self.remove_color_button = QPushButton("Remove", self)
        self.remove_color_button.clicked.connect(self._on_remove_color)
        edit_row.addWidget(self.remove_color_button)
        self.swap_prev_button = QPushButton("Swap <-", self)
        self.swap_prev_button.clicked.connect(lambda: self._on_swap_color(-1))
        edit_row.addWidget(self.swap_prev_button)
        self.swap_next_button = QPushButton("Swap ->", self)
        self.swap_next_button.clicked.connect(lambda: self._on_swap_color(1))
        edit_row.addWidget(self.swap_next_button)
        root_layout.addLayout(edit_row)

        actions_row = QHBoxLayout()
        self.save_palette_button = QPushButton("Save Preset", self)
        self.save_palette_button.clicked.connect(self._on_save_palette)
        actions_row.addWidget(self.save_palette_button)
        self.load_palette_button = QPushButton("Load Preset", self)
        self.load_palette_button.clicked.connect(self._on_load_palette)
        actions_row.addWidget(self.load_palette_button)
        root_layout.addLayout(actions_row)
        self.lock_active_slot_checkbox = QCheckBox("Lock Active Slot", self)
        self.lock_active_slot_checkbox.stateChanged.connect(self._on_lock_active_slot_toggled)
        root_layout.addWidget(self.lock_active_slot_checkbox)
        root_layout.addStretch(1)

        self._rebuild_color_buttons()

    def set_context(self, ctx: "AppContext") -> None:
        self._context = ctx
        self.refresh()

    def refresh(self) -> None:
        if self._context is None:
            return
        if len(self._buttons) != len(self._context.palette):
            self._rebuild_color_buttons()
        for idx, button in enumerate(self._buttons):
            rgb = self._context.palette[idx]
            selected = idx == self._context.active_color_index
            border = "2px solid #ffffff" if selected else "1px solid #444444"
            button.setStyleSheet(
                f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: {border};"
            )
        active = self._context.palette[self._context.active_color_index]
        self.r_spin.blockSignals(True)
        self.g_spin.blockSignals(True)
        self.b_spin.blockSignals(True)
        self.r_spin.setValue(active[0])
        self.g_spin.setValue(active[1])
        self.b_spin.setValue(active[2])
        self.r_spin.blockSignals(False)
        self.g_spin.blockSignals(False)
        self.b_spin.blockSignals(False)
        is_locked = self._context.is_palette_slot_locked(self._context.active_color_index)
        self.lock_active_slot_checkbox.blockSignals(True)
        self.lock_active_slot_checkbox.setChecked(is_locked)
        self.lock_active_slot_checkbox.blockSignals(False)

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
            "Palette Preset (*.json *.gpl);;JSON (*.json);;GIMP Palette (*.gpl);;All Files (*)",
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
            "Palette Preset (*.json *.gpl);;JSON (*.json);;GIMP Palette (*.gpl);;All Files (*)",
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

    def _on_rgb_changed(self, _value: int) -> None:
        if self._context is None:
            return
        idx = self._context.active_color_index
        if self._context.is_palette_slot_locked(idx):
            self.refresh()
            self.palette_status_message.emit(f"Color slot {idx} is locked")
            return
        self._context.palette[idx] = (self.r_spin.value(), self.g_spin.value(), self.b_spin.value())
        self.refresh()
        self.palette_status_message.emit(f"Edited color slot {idx}")

    def _on_add_color(self) -> None:
        if self._context is None:
            return
        base = self._context.palette[self._context.active_color_index]
        insert_at = self._context.active_color_index + 1
        shifted: set[int] = set()
        for slot in self._context.locked_palette_slots:
            shifted.add(slot + 1 if slot >= insert_at else slot)
        self._context.locked_palette_slots = shifted
        self._context.palette = add_palette_color(self._context.palette, base, index=insert_at)
        self._context.active_color_index = insert_at
        self.refresh()
        self.active_color_changed.emit(self._context.active_color_index)
        self.palette_status_message.emit("Added palette color")

    def _on_remove_color(self) -> None:
        if self._context is None:
            return
        if self._context.is_palette_slot_locked(self._context.active_color_index):
            QMessageBox.information(self, "Remove Color", "Active color slot is locked.")
            return
        try:
            self._context.palette = remove_palette_color(self._context.palette, self._context.active_color_index)
        except ValueError as exc:
            QMessageBox.information(self, "Remove Color", str(exc))
            return
        removed = self._context.active_color_index
        shifted: set[int] = set()
        for slot in self._context.locked_palette_slots:
            if slot == removed:
                continue
            shifted.add(slot - 1 if slot > removed else slot)
        self._context.locked_palette_slots = shifted
        self._context.active_color_index = clamp_active_color_index(
            self._context.active_color_index,
            len(self._context.palette),
        )
        self.refresh()
        self.active_color_changed.emit(self._context.active_color_index)
        self.palette_status_message.emit("Removed palette color")

    def _on_swap_color(self, direction: int) -> None:
        if self._context is None:
            return
        src = self._context.active_color_index
        dst = src + direction
        if dst < 0 or dst >= len(self._context.palette):
            return
        if self._context.is_palette_slot_locked(src) or self._context.is_palette_slot_locked(dst):
            QMessageBox.information(self, "Swap Color", "Locked color slots cannot be swapped.")
            return
        self._context.palette = swap_palette_colors(self._context.palette, src, dst)
        locked = self._context.locked_palette_slots
        src_locked = src in locked
        dst_locked = dst in locked
        if src_locked or dst_locked:
            locked.discard(src)
            locked.discard(dst)
            if src_locked:
                locked.add(dst)
            if dst_locked:
                locked.add(src)
        self._context.active_color_index = dst
        self.refresh()
        self.active_color_changed.emit(self._context.active_color_index)
        self.palette_status_message.emit("Swapped palette colors")

    def _on_lock_active_slot_toggled(self, state: int) -> None:
        if self._context is None:
            return
        slot = self._context.active_color_index
        locked = state != 0
        self._context.set_palette_slot_locked(slot, locked)
        self.palette_status_message.emit(
            f"{'Locked' if locked else 'Unlocked'} color slot {slot}"
        )

    def _rebuild_color_buttons(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._buttons = []
        swatch_count = 8 if self._context is None else len(self._context.palette)
        for idx in range(swatch_count):
            button = QPushButton("")
            button.setFixedSize(28, 28)
            button.clicked.connect(lambda _checked=False, i=idx: self._on_color_clicked(i))
            row = idx // 8
            col = idx % 8
            self.grid.addWidget(button, row, col)
            self._buttons.append(button)
