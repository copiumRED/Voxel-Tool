from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.app_context import AppContext


class InspectorPanel(QWidget):
    part_selection_changed = Signal(str)
    part_status_message = Signal(str)

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

        self.duplicate_part_button = QPushButton("Duplicate Part", self)
        self.duplicate_part_button.clicked.connect(self._on_duplicate_part)
        buttons_layout.addWidget(self.duplicate_part_button)

        self.delete_part_button = QPushButton("Delete Part", self)
        self.delete_part_button.clicked.connect(self._on_delete_part)
        buttons_layout.addWidget(self.delete_part_button)

        layout.addLayout(buttons_layout)

        flags_layout = QHBoxLayout()
        self.visible_checkbox = QCheckBox("Visible", self)
        self.visible_checkbox.stateChanged.connect(self._on_visible_toggled)
        flags_layout.addWidget(self.visible_checkbox)

        self.locked_checkbox = QCheckBox("Locked", self)
        self.locked_checkbox.stateChanged.connect(self._on_locked_toggled)
        flags_layout.addWidget(self.locked_checkbox)
        layout.addLayout(flags_layout)
        layout.addStretch(1)

    def set_context(self, context: AppContext) -> None:
        self._context = context
        self.refresh()

    def refresh(self) -> None:
        if self._context is None:
            return

        active_part_id = self._context.active_part_id
        active_part = self._context.active_part
        self.part_list.blockSignals(True)
        self.part_list.clear()
        for part_id, part in self._context.current_project.scene.parts.items():
            item = QListWidgetItem(part.name)
            item.setData(Qt.UserRole, part_id)
            self.part_list.addItem(item)
            if part_id == active_part_id:
                self.part_list.setCurrentItem(item)
        self.part_list.blockSignals(False)

        self.visible_checkbox.blockSignals(True)
        self.locked_checkbox.blockSignals(True)
        self.visible_checkbox.setChecked(active_part.visible)
        self.locked_checkbox.setChecked(active_part.locked)
        self.visible_checkbox.blockSignals(False)
        self.locked_checkbox.blockSignals(False)

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

    def _on_duplicate_part(self) -> None:
        if self._context is None:
            return
        current_item = self.part_list.currentItem()
        if current_item is None:
            return
        source_part_id = current_item.data(Qt.UserRole)
        if not isinstance(source_part_id, str):
            return

        source_name = current_item.text().strip()
        default_name = f"{source_name} Copy" if source_name else "Part Copy"
        name, accepted = QInputDialog.getText(self, "Duplicate Part", "New part name:", text=default_name)
        if not accepted:
            return
        duplicate_name = name.strip()
        if not duplicate_name:
            return

        duplicated = self._context.current_project.scene.duplicate_part(source_part_id, new_name=duplicate_name)
        self.refresh()
        self.part_selection_changed.emit(duplicated.part_id)
        self.part_status_message.emit(f"Duplicated part: {duplicate_name}")

    def _on_delete_part(self) -> None:
        if self._context is None:
            return
        current_item = self.part_list.currentItem()
        if current_item is None:
            return
        part_id = current_item.data(Qt.UserRole)
        if not isinstance(part_id, str):
            return
        part_name = current_item.text().strip() or part_id

        scene = self._context.current_project.scene
        if len(scene.parts) <= 1:
            QMessageBox.information(self, "Delete Part", "At least one part must remain in the scene.")
            return
        answer = QMessageBox.question(
            self,
            "Delete Part",
            f"Delete part '{part_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        next_active_part_id = scene.delete_part(part_id)
        self.refresh()
        self.part_selection_changed.emit(next_active_part_id)
        self.part_status_message.emit(f"Deleted part: {part_name}")

    def _on_visible_toggled(self, state: int) -> None:
        if self._context is None:
            return
        part = self._context.active_part
        part.visible = state == Qt.Checked
        self.part_status_message.emit(
            f"Part visibility: {'on' if part.visible else 'off'} ({part.name})"
        )
        self.refresh()

    def _on_locked_toggled(self, state: int) -> None:
        if self._context is None:
            return
        part = self._context.active_part
        part.locked = state == Qt.Checked
        self.part_status_message.emit(f"Part lock: {'on' if part.locked else 'off'} ({part.name})")
        self.refresh()
