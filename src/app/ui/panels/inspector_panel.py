from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.app_context import AppContext


class InspectorPanel(QWidget):
    part_selection_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Parts"))

        self.part_list = QListWidget(self)
        self.part_list.currentItemChanged.connect(self._on_current_part_changed)
        layout.addWidget(self.part_list)

        buttons_layout = QHBoxLayout()
        self.add_part_button = QPushButton("Add Part", self)
        self.add_part_button.clicked.connect(self._on_add_part)
        buttons_layout.addWidget(self.add_part_button)

        self.rename_part_button = QPushButton("Rename Part", self)
        self.rename_part_button.clicked.connect(self._on_rename_part)
        buttons_layout.addWidget(self.rename_part_button)

        layout.addLayout(buttons_layout)
        layout.addStretch(1)

    def set_context(self, context: AppContext) -> None:
        self._context = context
        self.refresh()

    def refresh(self) -> None:
        if self._context is None:
            return

        active_part_id = self._context.active_part_id
        self.part_list.blockSignals(True)
        self.part_list.clear()
        for part_id, part in self._context.current_project.scene.parts.items():
            item = QListWidgetItem(part.name)
            item.setData(Qt.UserRole, part_id)
            self.part_list.addItem(item)
            if part_id == active_part_id:
                self.part_list.setCurrentItem(item)
        self.part_list.blockSignals(False)

    def _on_add_part(self) -> None:
        if self._context is None:
            return
        scene = self._context.current_project.scene
        part = scene.add_part(f"Part {len(scene.parts) + 1}")
        scene.set_active_part(part.part_id)
        self.refresh()
        self.part_selection_changed.emit(part.part_id)

    def _on_rename_part(self) -> None:
        if self._context is None:
            return
        current_item = self.part_list.currentItem()
        if current_item is None:
            return
        part_id = current_item.data(Qt.UserRole)
        if not isinstance(part_id, str):
            return

        current_name = current_item.text()
        name, accepted = QInputDialog.getText(self, "Rename Part", "Part name:", text=current_name)
        if not accepted:
            return
        stripped = name.strip()
        if not stripped:
            return
        self._context.current_project.scene.rename_part(part_id, stripped)
        self.refresh()

    def _on_current_part_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if self._context is None or current is None:
            return
        part_id = current.data(Qt.UserRole)
        if not isinstance(part_id, str):
            return
        self._context.set_active_part(part_id)
        self.part_selection_changed.emit(part_id)
