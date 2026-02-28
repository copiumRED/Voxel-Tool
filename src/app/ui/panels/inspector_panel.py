from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
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
        self.move_up_button = QPushButton("Move Up", self)
        self.move_up_button.clicked.connect(lambda: self._on_move_part(-1))
        buttons_layout.addWidget(self.move_up_button)
        self.move_down_button = QPushButton("Move Down", self)
        self.move_down_button.clicked.connect(lambda: self._on_move_part(1))
        buttons_layout.addWidget(self.move_down_button)

        layout.addLayout(buttons_layout)

        flags_layout = QHBoxLayout()
        self.visible_checkbox = QCheckBox("Visible", self)
        self.visible_checkbox.stateChanged.connect(self._on_visible_toggled)
        flags_layout.addWidget(self.visible_checkbox)

        self.locked_checkbox = QCheckBox("Locked", self)
        self.locked_checkbox.stateChanged.connect(self._on_locked_toggled)
        flags_layout.addWidget(self.locked_checkbox)
        layout.addLayout(flags_layout)

        transform_layout = QFormLayout()
        self.position_x = self._create_transform_spin()
        self.position_y = self._create_transform_spin()
        self.position_z = self._create_transform_spin()
        self.rotation_x = self._create_transform_spin(min_value=-360.0, max_value=360.0)
        self.rotation_y = self._create_transform_spin(min_value=-360.0, max_value=360.0)
        self.rotation_z = self._create_transform_spin(min_value=-360.0, max_value=360.0)
        self.scale_x = self._create_transform_spin(min_value=0.01, max_value=100.0, default=1.0)
        self.scale_y = self._create_transform_spin(min_value=0.01, max_value=100.0, default=1.0)
        self.scale_z = self._create_transform_spin(min_value=0.01, max_value=100.0, default=1.0)
        self.position_x.valueChanged.connect(lambda _: self._on_transform_changed())
        self.position_y.valueChanged.connect(lambda _: self._on_transform_changed())
        self.position_z.valueChanged.connect(lambda _: self._on_transform_changed())
        self.rotation_x.valueChanged.connect(lambda _: self._on_transform_changed())
        self.rotation_y.valueChanged.connect(lambda _: self._on_transform_changed())
        self.rotation_z.valueChanged.connect(lambda _: self._on_transform_changed())
        self.scale_x.valueChanged.connect(lambda _: self._on_transform_changed())
        self.scale_y.valueChanged.connect(lambda _: self._on_transform_changed())
        self.scale_z.valueChanged.connect(lambda _: self._on_transform_changed())
        transform_layout.addRow("Pos X", self.position_x)
        transform_layout.addRow("Pos Y", self.position_y)
        transform_layout.addRow("Pos Z", self.position_z)
        transform_layout.addRow("Rot X", self.rotation_x)
        transform_layout.addRow("Rot Y", self.rotation_y)
        transform_layout.addRow("Rot Z", self.rotation_z)
        transform_layout.addRow("Scale X", self.scale_x)
        transform_layout.addRow("Scale Y", self.scale_y)
        transform_layout.addRow("Scale Z", self.scale_z)
        layout.addLayout(transform_layout)
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
        for part_id, part in self._context.current_project.scene.iter_parts_ordered():
            item = QListWidgetItem(part.name)
            item.setData(Qt.UserRole, part_id)
            self.part_list.addItem(item)
            if part_id == active_part_id:
                self.part_list.setCurrentItem(item)
        self.part_list.blockSignals(False)

        self.visible_checkbox.blockSignals(True)
        self.locked_checkbox.blockSignals(True)
        self._set_transform_signals_blocked(True)
        self.visible_checkbox.setChecked(active_part.visible)
        self.locked_checkbox.setChecked(active_part.locked)
        self.position_x.setValue(active_part.position[0])
        self.position_y.setValue(active_part.position[1])
        self.position_z.setValue(active_part.position[2])
        self.rotation_x.setValue(active_part.rotation[0])
        self.rotation_y.setValue(active_part.rotation[1])
        self.rotation_z.setValue(active_part.rotation[2])
        self.scale_x.setValue(active_part.scale[0])
        self.scale_y.setValue(active_part.scale[1])
        self.scale_z.setValue(active_part.scale[2])
        self.visible_checkbox.blockSignals(False)
        self.locked_checkbox.blockSignals(False)
        self._set_transform_signals_blocked(False)

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

    def _on_transform_changed(self) -> None:
        if self._context is None:
            return
        part = self._context.active_part
        part.position = (self.position_x.value(), self.position_y.value(), self.position_z.value())
        part.rotation = (self.rotation_x.value(), self.rotation_y.value(), self.rotation_z.value())
        part.scale = (self.scale_x.value(), self.scale_y.value(), self.scale_z.value())
        self.part_status_message.emit(
            "Part transform updated: "
            f"pos={part.position} rot={part.rotation} scale={part.scale} ({part.name})"
        )

    def _on_move_part(self, direction: int) -> None:
        if self._context is None:
            return
        current_item = self.part_list.currentItem()
        if current_item is None:
            return
        part_id = current_item.data(Qt.UserRole)
        if not isinstance(part_id, str):
            return
        moved = self._context.current_project.scene.move_part(part_id, direction)
        if not moved:
            return
        self.refresh()
        self.part_list.setCurrentRow(
            next(
                i
                for i in range(self.part_list.count())
                if self.part_list.item(i).data(Qt.UserRole) == part_id
            )
        )
        self.part_status_message.emit(f"Part order updated: {self._context.active_part.name}")

    @staticmethod
    def _create_transform_spin(
        *,
        min_value: float = -999.0,
        max_value: float = 999.0,
        default: float = 0.0,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_value, max_value)
        spin.setDecimals(2)
        spin.setSingleStep(0.1)
        spin.setValue(default)
        return spin

    def _set_transform_signals_blocked(self, blocked: bool) -> None:
        for control in (
            self.position_x,
            self.position_y,
            self.position_z,
            self.rotation_x,
            self.rotation_y,
            self.rotation_z,
            self.scale_x,
            self.scale_y,
            self.scale_z,
        ):
            control.blockSignals(blocked)
