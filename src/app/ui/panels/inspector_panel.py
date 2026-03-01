from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.app_context import AppContext


class _DragScrubLabel(QLabel):
    scrub_delta = Signal(int)

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.SizeHorCursor)
        self.setToolTip("Drag horizontally to scrub value")
        self._dragging = False
        self._last_x = 0

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_x = event.globalPosition().toPoint().x()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._dragging:
            current_x = event.globalPosition().toPoint().x()
            delta = current_x - self._last_x
            if delta != 0:
                self._last_x = current_x
                self.scrub_delta.emit(delta)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)


class InspectorPanel(QWidget):
    part_selection_changed = Signal(str)
    part_status_message = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Parts"))
        self.part_filter_input = QLineEdit(self)
        self.part_filter_input.setPlaceholderText("Filter parts...")
        self.part_filter_input.textChanged.connect(lambda _text: self.refresh())
        layout.addWidget(self.part_filter_input)

        self.part_list = QListWidget(self)
        self.part_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
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

        multi_buttons_layout = QHBoxLayout()
        self.show_selected_button = QPushButton("Show Selected", self)
        self.show_selected_button.clicked.connect(lambda: self._on_set_selected_parts_visible(True))
        multi_buttons_layout.addWidget(self.show_selected_button)
        self.hide_selected_button = QPushButton("Hide Selected", self)
        self.hide_selected_button.clicked.connect(lambda: self._on_set_selected_parts_visible(False))
        multi_buttons_layout.addWidget(self.hide_selected_button)
        self.lock_selected_button = QPushButton("Lock Selected", self)
        self.lock_selected_button.clicked.connect(lambda: self._on_set_selected_parts_locked(True))
        multi_buttons_layout.addWidget(self.lock_selected_button)
        self.unlock_selected_button = QPushButton("Unlock Selected", self)
        self.unlock_selected_button.clicked.connect(lambda: self._on_set_selected_parts_locked(False))
        multi_buttons_layout.addWidget(self.unlock_selected_button)
        self.delete_selected_button = QPushButton("Delete Selected", self)
        self.delete_selected_button.clicked.connect(self._on_delete_selected_parts)
        multi_buttons_layout.addWidget(self.delete_selected_button)
        layout.addLayout(multi_buttons_layout)

        flags_layout = QHBoxLayout()
        self.visible_checkbox = QCheckBox("Visible", self)
        self.visible_checkbox.stateChanged.connect(self._on_visible_toggled)
        flags_layout.addWidget(self.visible_checkbox)

        self.locked_checkbox = QCheckBox("Locked", self)
        self.locked_checkbox.stateChanged.connect(self._on_locked_toggled)
        flags_layout.addWidget(self.locked_checkbox)
        layout.addLayout(flags_layout)

        layout.addWidget(QLabel("Groups"))
        self.group_filter_input = QLineEdit(self)
        self.group_filter_input.setPlaceholderText("Filter groups...")
        self.group_filter_input.textChanged.connect(lambda _text: self.refresh())
        layout.addWidget(self.group_filter_input)
        self.group_list = QListWidget(self)
        self.group_list.currentItemChanged.connect(self._on_current_group_changed)
        layout.addWidget(self.group_list)

        group_buttons_layout = QHBoxLayout()
        self.add_group_button = QPushButton("Add Group", self)
        self.add_group_button.clicked.connect(self._on_add_group)
        group_buttons_layout.addWidget(self.add_group_button)
        self.delete_group_button = QPushButton("Delete Group", self)
        self.delete_group_button.clicked.connect(self._on_delete_group)
        group_buttons_layout.addWidget(self.delete_group_button)
        self.assign_group_button = QPushButton("Assign Active Part", self)
        self.assign_group_button.clicked.connect(self._on_assign_active_part_to_group)
        group_buttons_layout.addWidget(self.assign_group_button)
        self.unassign_group_button = QPushButton("Unassign Active Part", self)
        self.unassign_group_button.clicked.connect(self._on_unassign_active_part_from_group)
        group_buttons_layout.addWidget(self.unassign_group_button)
        layout.addLayout(group_buttons_layout)

        group_flags_layout = QHBoxLayout()
        self.group_visible_checkbox = QCheckBox("Group Visible", self)
        self.group_visible_checkbox.stateChanged.connect(self._on_group_visible_toggled)
        group_flags_layout.addWidget(self.group_visible_checkbox)
        self.group_locked_checkbox = QCheckBox("Group Locked", self)
        self.group_locked_checkbox.stateChanged.connect(self._on_group_locked_toggled)
        group_flags_layout.addWidget(self.group_locked_checkbox)
        layout.addLayout(group_flags_layout)
        self.part_groups_label = QLabel(self)
        self.part_groups_label.setWordWrap(True)
        layout.addWidget(self.part_groups_label)

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
        transform_layout.addRow(self._create_transform_row_label("Pos X", self.position_x), self.position_x)
        transform_layout.addRow(self._create_transform_row_label("Pos Y", self.position_y), self.position_y)
        transform_layout.addRow(self._create_transform_row_label("Pos Z", self.position_z), self.position_z)
        transform_layout.addRow(self._create_transform_row_label("Rot X", self.rotation_x), self.rotation_x)
        transform_layout.addRow(self._create_transform_row_label("Rot Y", self.rotation_y), self.rotation_y)
        transform_layout.addRow(self._create_transform_row_label("Rot Z", self.rotation_z), self.rotation_z)
        transform_layout.addRow(self._create_transform_row_label("Scale X", self.scale_x), self.scale_x)
        transform_layout.addRow(self._create_transform_row_label("Scale Y", self.scale_y), self.scale_y)
        transform_layout.addRow(self._create_transform_row_label("Scale Z", self.scale_z), self.scale_z)
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
        part_filter = self.part_filter_input.text()
        for part_id, part in self._context.current_project.scene.iter_parts_ordered():
            if not self._matches_filter_text(part.name, part_filter):
                continue
            item = QListWidgetItem(part.name)
            item.setData(Qt.UserRole, part_id)
            self.part_list.addItem(item)
            if part_id == active_part_id:
                self.part_list.setCurrentItem(item)
        self.part_list.blockSignals(False)
        self.group_list.blockSignals(True)
        self.group_list.clear()
        group_filter = self.group_filter_input.text()
        for group_id, group in self._context.current_project.scene.iter_groups_ordered():
            if not self._matches_filter_text(group.name, group_filter):
                continue
            item = QListWidgetItem(group.name)
            item.setData(Qt.UserRole, group_id)
            self.group_list.addItem(item)
        self.group_list.blockSignals(False)

        self.visible_checkbox.blockSignals(True)
        self.locked_checkbox.blockSignals(True)
        self.group_visible_checkbox.blockSignals(True)
        self.group_locked_checkbox.blockSignals(True)
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
        selected_group = self._selected_group()
        if selected_group is not None:
            self.group_visible_checkbox.setChecked(selected_group.visible)
            self.group_locked_checkbox.setChecked(selected_group.locked)
        else:
            self.group_visible_checkbox.setChecked(False)
            self.group_locked_checkbox.setChecked(False)
        self.group_visible_checkbox.blockSignals(False)
        self.group_locked_checkbox.blockSignals(False)
        self._set_transform_signals_blocked(False)
        memberships = self._context.current_project.scene.group_names_for_part(active_part.part_id)
        if memberships:
            self.part_groups_label.setText(f"Active Part Groups: {', '.join(memberships)}")
        else:
            self.part_groups_label.setText("Active Part Groups: (none)")

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

    def _selected_part_ids(self) -> list[str]:
        selected: list[str] = []
        for item in self.part_list.selectedItems():
            part_id = item.data(Qt.UserRole)
            if isinstance(part_id, str):
                selected.append(part_id)
        if selected:
            return selected
        current_item = self.part_list.currentItem()
        if current_item is None:
            return []
        part_id = current_item.data(Qt.UserRole)
        if isinstance(part_id, str):
            return [part_id]
        return []

    def _on_set_selected_parts_visible(self, visible: bool) -> None:
        if self._context is None:
            return
        selected_ids = self._selected_part_ids()
        if not selected_ids:
            return
        updated = self._context.current_project.scene.set_parts_visible(selected_ids, visible)
        if not updated:
            return
        self.part_status_message.emit(f"Updated visibility for {len(updated)} selected part(s).")
        self.refresh()

    def _on_set_selected_parts_locked(self, locked: bool) -> None:
        if self._context is None:
            return
        selected_ids = self._selected_part_ids()
        if not selected_ids:
            return
        updated = self._context.current_project.scene.set_parts_locked(selected_ids, locked)
        if not updated:
            return
        self.part_status_message.emit(f"Updated lock for {len(updated)} selected part(s).")
        self.refresh()

    def _on_delete_selected_parts(self) -> None:
        if self._context is None:
            return
        selected_ids = self._selected_part_ids()
        if not selected_ids:
            return
        if len(selected_ids) <= 1:
            self._on_delete_part()
            return
        if len(self._context.current_project.scene.parts) - len({*selected_ids}) < 1:
            QMessageBox.information(self, "Delete Selected", "At least one part must remain in the scene.")
            return
        answer = QMessageBox.question(
            self,
            "Delete Selected Parts",
            f"Delete {len(selected_ids)} selected parts?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        next_active_part_id = self._context.current_project.scene.delete_parts(selected_ids)
        self.refresh()
        self.part_selection_changed.emit(next_active_part_id)
        self.part_status_message.emit(f"Deleted {len(selected_ids)} selected part(s).")

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

    def _selected_group(self):
        if self._context is None:
            return None
        current_item = self.group_list.currentItem()
        if current_item is None:
            return None
        group_id = current_item.data(Qt.UserRole)
        if not isinstance(group_id, str):
            return None
        return self._context.current_project.scene.groups.get(group_id)

    def _on_current_group_changed(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        del previous
        if self._context is None or current is None:
            return
        group = self._selected_group()
        self.group_visible_checkbox.blockSignals(True)
        self.group_locked_checkbox.blockSignals(True)
        if group is not None:
            self.group_visible_checkbox.setChecked(group.visible)
            self.group_locked_checkbox.setChecked(group.locked)
        else:
            self.group_visible_checkbox.setChecked(False)
            self.group_locked_checkbox.setChecked(False)
        self.group_visible_checkbox.blockSignals(False)
        self.group_locked_checkbox.blockSignals(False)

    def _on_add_group(self) -> None:
        if self._context is None:
            return
        name, accepted = QInputDialog.getText(self, "Add Group", "Group name:", text="Group 1")
        if not accepted:
            return
        group_name = name.strip()
        if not group_name:
            return
        group = self._context.current_project.scene.create_group(group_name)
        self.refresh()
        for row in range(self.group_list.count()):
            item = self.group_list.item(row)
            if item.data(Qt.UserRole) == group.group_id:
                self.group_list.setCurrentRow(row)
                break
        self.part_status_message.emit(f"Created group: {group.name}")

    def _on_delete_group(self) -> None:
        if self._context is None:
            return
        current_item = self.group_list.currentItem()
        if current_item is None:
            return
        group_id = current_item.data(Qt.UserRole)
        if not isinstance(group_id, str):
            return
        group_name = current_item.text().strip() or group_id
        self._context.current_project.scene.delete_group(group_id)
        self.refresh()
        self.part_status_message.emit(f"Deleted group: {group_name}")

    def _on_assign_active_part_to_group(self) -> None:
        if self._context is None:
            return
        group = self._selected_group()
        if group is None:
            return
        part = self._context.active_part
        self._context.current_project.scene.assign_part_to_group(part.part_id, group.group_id)
        self.part_status_message.emit(f"Assigned {part.name} -> {group.name}")
        self.refresh()

    def _on_unassign_active_part_from_group(self) -> None:
        if self._context is None:
            return
        group = self._selected_group()
        if group is None:
            return
        part = self._context.active_part
        self._context.current_project.scene.unassign_part_from_group(part.part_id, group.group_id)
        self.part_status_message.emit(f"Unassigned {part.name} from {group.name}")
        self.refresh()

    def _on_group_visible_toggled(self, state: int) -> None:
        if self._context is None:
            return
        group = self._selected_group()
        if group is None:
            return
        visible = state == Qt.Checked
        self._context.current_project.scene.set_group_visible(group.group_id, visible)
        self.part_status_message.emit(f"Group visibility: {'on' if visible else 'off'} ({group.name})")
        self.refresh()

    def _on_group_locked_toggled(self, state: int) -> None:
        if self._context is None:
            return
        group = self._selected_group()
        if group is None:
            return
        locked = state == Qt.Checked
        self._context.current_project.scene.set_group_locked(group.group_id, locked)
        self.part_status_message.emit(f"Group lock: {'on' if locked else 'off'} ({group.name})")
        self.refresh()

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
    def _matches_filter_text(label: str, text_filter: str) -> bool:
        needle = str(text_filter).strip().lower()
        if not needle:
            return True
        return needle in str(label).strip().lower()

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

    def _create_transform_row_label(self, text: str, spin: QDoubleSpinBox) -> QLabel:
        label = _DragScrubLabel(text, self)
        label.scrub_delta.connect(lambda pixel_delta: self._on_transform_scrub(spin, pixel_delta))
        return label

    def _on_transform_scrub(self, spin: QDoubleSpinBox, pixel_delta: int) -> None:
        delta = self._transform_scrub_delta_for_pixels(pixel_delta, spin.singleStep())
        next_value = self._apply_scrubbed_value(spin.value(), delta, spin.minimum(), spin.maximum())
        spin.setValue(next_value)

    @staticmethod
    def _transform_scrub_delta_for_pixels(pixel_delta: int, single_step: float) -> float:
        return float(pixel_delta) * float(single_step)

    @staticmethod
    def _apply_scrubbed_value(value: float, delta: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(max_value, value + delta))

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
