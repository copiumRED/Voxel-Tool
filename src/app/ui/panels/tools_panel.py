from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.app_context import AppContext


class ToolsPanel(QWidget):
    tool_mode_changed = Signal(str)
    tool_shape_changed = Signal(str)
    mirror_changed = Signal(str, bool)
    mirror_offset_changed = Signal(str, int)
    brush_profile_changed = Signal(int, str)
    pick_mode_changed = Signal(str)
    edit_plane_changed = Signal(str)
    fill_connectivity_changed = Signal(str)
    selection_mode_changed = Signal(bool)
    duplicate_selected_requested = Signal(int, int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Plane Tool"))

        self.brush_shape_radio = QRadioButton("Brush", self)
        self.box_shape_radio = QRadioButton("Box", self)
        self.line_shape_radio = QRadioButton("Line", self)
        self.fill_shape_radio = QRadioButton("Fill", self)
        self.brush_shape_radio.setChecked(True)
        self.brush_shape_radio.toggled.connect(self._on_shape_toggled)
        self.box_shape_radio.toggled.connect(self._on_shape_toggled)
        self.line_shape_radio.toggled.connect(self._on_shape_toggled)
        self.fill_shape_radio.toggled.connect(self._on_shape_toggled)

        layout.addWidget(self.brush_shape_radio)
        layout.addWidget(self.box_shape_radio)
        layout.addWidget(self.line_shape_radio)
        layout.addWidget(self.fill_shape_radio)
        layout.addWidget(QLabel("Brush Profile"))
        self.brush_size_spin = QSpinBox(self)
        self.brush_size_spin.setRange(1, 3)
        self.brush_size_spin.setValue(1)
        self.brush_size_spin.setPrefix("Size ")
        self.brush_size_spin.valueChanged.connect(self._on_brush_size_changed)
        layout.addWidget(self.brush_size_spin)

        self.brush_shape_combo = QComboBox(self)
        self.brush_shape_combo.addItems(["Cube", "Sphere"])
        self.brush_shape_combo.currentTextChanged.connect(self._on_brush_profile_changed)
        layout.addWidget(self.brush_shape_combo)
        self.pick_mode_combo = QComboBox(self)
        self.pick_mode_combo.addItems(["Plane Lock", "Surface"])
        self.pick_mode_combo.currentTextChanged.connect(self._on_pick_mode_changed)
        layout.addWidget(self.pick_mode_combo)
        self.edit_plane_combo = QComboBox(self)
        self.edit_plane_combo.addItems(["XY", "YZ", "XZ"])
        self.edit_plane_combo.currentTextChanged.connect(self._on_edit_plane_changed)
        layout.addWidget(self.edit_plane_combo)
        self.fill_connectivity_combo = QComboBox(self)
        self.fill_connectivity_combo.addItems(["Plane", "3D"])
        self.fill_connectivity_combo.currentTextChanged.connect(self._on_fill_connectivity_changed)
        layout.addWidget(self.fill_connectivity_combo)
        self.selection_mode_checkbox = QCheckBox("Voxel Selection Mode", self)
        self.selection_mode_checkbox.stateChanged.connect(self._on_selection_mode_toggled)
        layout.addWidget(self.selection_mode_checkbox)
        layout.addWidget(QLabel("Selection Duplicate"))
        duplicate_offset_row = QHBoxLayout()
        self.duplicate_offset_x_spin = QSpinBox(self)
        self.duplicate_offset_y_spin = QSpinBox(self)
        self.duplicate_offset_z_spin = QSpinBox(self)
        for spin in (self.duplicate_offset_x_spin, self.duplicate_offset_y_spin, self.duplicate_offset_z_spin):
            spin.setRange(-64, 64)
        self.duplicate_offset_x_spin.setValue(1)
        self.duplicate_offset_x_spin.setPrefix("X ")
        self.duplicate_offset_y_spin.setPrefix("Y ")
        self.duplicate_offset_z_spin.setPrefix("Z ")
        duplicate_offset_row.addWidget(self.duplicate_offset_x_spin)
        duplicate_offset_row.addWidget(self.duplicate_offset_y_spin)
        duplicate_offset_row.addWidget(self.duplicate_offset_z_spin)
        layout.addLayout(duplicate_offset_row)
        self.duplicate_selected_button = QPushButton("Duplicate Selected Voxels", self)
        self.duplicate_selected_button.clicked.connect(self._on_duplicate_selected_clicked)
        layout.addWidget(self.duplicate_selected_button)
        layout.addWidget(QLabel("Action"))

        self.paint_radio = QRadioButton("Paint", self)
        self.erase_radio = QRadioButton("Erase", self)
        self.paint_radio.setChecked(True)

        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self.paint_radio)
        self._mode_group.addButton(self.erase_radio)

        self.paint_radio.toggled.connect(self._on_mode_toggled)
        self.erase_radio.toggled.connect(self._on_mode_toggled)

        layout.addWidget(self.paint_radio)
        layout.addWidget(self.erase_radio)
        layout.addWidget(QLabel("Mirror"))
        self.mirror_x_checkbox = QCheckBox("Mirror X", self)
        self.mirror_y_checkbox = QCheckBox("Mirror Y", self)
        self.mirror_z_checkbox = QCheckBox("Mirror Z", self)
        self.mirror_x_offset = QSpinBox(self)
        self.mirror_y_offset = QSpinBox(self)
        self.mirror_z_offset = QSpinBox(self)
        for spin in (self.mirror_x_offset, self.mirror_y_offset, self.mirror_z_offset):
            spin.setRange(-128, 128)
            spin.setPrefix("offset ")
        self.mirror_x_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("x", checked))
        self.mirror_y_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("y", checked))
        self.mirror_z_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("z", checked))
        self.mirror_x_offset.valueChanged.connect(lambda value: self._on_mirror_offset_changed("x", value))
        self.mirror_y_offset.valueChanged.connect(lambda value: self._on_mirror_offset_changed("y", value))
        self.mirror_z_offset.valueChanged.connect(lambda value: self._on_mirror_offset_changed("z", value))

        x_row = QHBoxLayout()
        x_row.addWidget(self.mirror_x_checkbox)
        x_row.addWidget(self.mirror_x_offset)
        layout.addLayout(x_row)

        y_row = QHBoxLayout()
        y_row.addWidget(self.mirror_y_checkbox)
        y_row.addWidget(self.mirror_y_offset)
        layout.addLayout(y_row)

        z_row = QHBoxLayout()
        z_row.addWidget(self.mirror_z_checkbox)
        z_row.addWidget(self.mirror_z_offset)
        layout.addLayout(z_row)

        self.hints_label = QLabel(self)
        self.hints_label.setWordWrap(True)
        self.hints_label.setStyleSheet("color: #d8d8d8;")
        layout.addWidget(self.hints_label)
        layout.addStretch(1)

    def set_context(self, context: AppContext) -> None:
        self._context = context
        self.refresh()

    def refresh(self) -> None:
        if self._context is None:
            return
        self.paint_radio.blockSignals(True)
        self.erase_radio.blockSignals(True)
        self.brush_shape_radio.blockSignals(True)
        self.box_shape_radio.blockSignals(True)
        self.line_shape_radio.blockSignals(True)
        self.fill_shape_radio.blockSignals(True)
        self.mirror_x_checkbox.blockSignals(True)
        self.mirror_y_checkbox.blockSignals(True)
        self.mirror_z_checkbox.blockSignals(True)
        self.mirror_x_offset.blockSignals(True)
        self.mirror_y_offset.blockSignals(True)
        self.mirror_z_offset.blockSignals(True)
        self.brush_size_spin.blockSignals(True)
        self.brush_shape_combo.blockSignals(True)
        self.pick_mode_combo.blockSignals(True)
        self.edit_plane_combo.blockSignals(True)
        self.fill_connectivity_combo.blockSignals(True)
        self.selection_mode_checkbox.blockSignals(True)
        self.paint_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_PAINT)
        self.erase_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_ERASE)
        self.brush_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BRUSH)
        self.box_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BOX)
        self.line_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_LINE)
        self.fill_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_FILL)
        self.mirror_x_checkbox.setChecked(self._context.mirror_x_enabled)
        self.mirror_y_checkbox.setChecked(self._context.mirror_y_enabled)
        self.mirror_z_checkbox.setChecked(self._context.mirror_z_enabled)
        self.mirror_x_offset.setValue(self._context.mirror_x_offset)
        self.mirror_y_offset.setValue(self._context.mirror_y_offset)
        self.mirror_z_offset.setValue(self._context.mirror_z_offset)
        self.brush_size_spin.setValue(self._context.brush_size)
        self.brush_shape_combo.setCurrentText(self._context.brush_shape.capitalize())
        pick_mode_label = "Plane Lock" if self._context.pick_mode == AppContext.PICK_MODE_PLANE_LOCK else "Surface"
        self.pick_mode_combo.setCurrentText(pick_mode_label)
        self.edit_plane_combo.setCurrentText(self._context.edit_plane.upper())
        fill_mode = "3D" if self._context.fill_connectivity == AppContext.FILL_CONNECTIVITY_VOLUME else "Plane"
        self.fill_connectivity_combo.setCurrentText(fill_mode)
        self.selection_mode_checkbox.setChecked(self._context.voxel_selection_mode)
        self.paint_radio.blockSignals(False)
        self.erase_radio.blockSignals(False)
        self.brush_shape_radio.blockSignals(False)
        self.box_shape_radio.blockSignals(False)
        self.line_shape_radio.blockSignals(False)
        self.fill_shape_radio.blockSignals(False)
        self.mirror_x_checkbox.blockSignals(False)
        self.mirror_y_checkbox.blockSignals(False)
        self.mirror_z_checkbox.blockSignals(False)
        self.mirror_x_offset.blockSignals(False)
        self.mirror_y_offset.blockSignals(False)
        self.mirror_z_offset.blockSignals(False)
        self.brush_size_spin.blockSignals(False)
        self.brush_shape_combo.blockSignals(False)
        self.pick_mode_combo.blockSignals(False)
        self.edit_plane_combo.blockSignals(False)
        self.fill_connectivity_combo.blockSignals(False)
        self.selection_mode_checkbox.blockSignals(False)
        is_brush = self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BRUSH
        self.brush_size_spin.setEnabled(is_brush)
        self.brush_shape_combo.setEnabled(is_brush)
        self.pick_mode_combo.setEnabled(is_brush)
        self.edit_plane_combo.setEnabled(True)
        self.fill_connectivity_combo.setEnabled(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_FILL)
        self.duplicate_selected_button.setEnabled(bool(self._context.selected_voxels))
        self.hints_label.setText(self._build_hint_text())

    def _on_mode_toggled(self, checked: bool) -> None:
        if not checked or self._context is None:
            return
        mode = AppContext.TOOL_MODE_PAINT if self.paint_radio.isChecked() else AppContext.TOOL_MODE_ERASE
        self._context.set_voxel_tool_mode(mode)
        self.tool_mode_changed.emit(mode)

    def _on_shape_toggled(self, checked: bool) -> None:
        if not checked or self._context is None:
            return
        if self.brush_shape_radio.isChecked():
            shape = AppContext.TOOL_SHAPE_BRUSH
        elif self.box_shape_radio.isChecked():
            shape = AppContext.TOOL_SHAPE_BOX
        elif self.line_shape_radio.isChecked():
            shape = AppContext.TOOL_SHAPE_LINE
        else:
            shape = AppContext.TOOL_SHAPE_FILL
        self._context.set_voxel_tool_shape(shape)
        self.tool_shape_changed.emit(shape)

    def _on_mirror_toggled(self, axis: str, checked: bool) -> None:
        if self._context is None:
            return
        self._context.set_mirror_axis(axis, checked)
        self.mirror_changed.emit(axis, checked)

    def _on_mirror_offset_changed(self, axis: str, value: int) -> None:
        if self._context is None:
            return
        self._context.set_mirror_offset(axis, value)
        self.mirror_offset_changed.emit(axis, value)

    def _on_brush_size_changed(self, value: int) -> None:
        if self._context is None:
            return
        self._context.set_brush_size(value)
        self.brush_profile_changed.emit(self._context.brush_size, self._context.brush_shape)

    def _on_brush_profile_changed(self, value: str) -> None:
        if self._context is None:
            return
        self._context.set_brush_shape(value.lower())
        self.brush_profile_changed.emit(self._context.brush_size, self._context.brush_shape)

    def _on_pick_mode_changed(self, value: str) -> None:
        if self._context is None:
            return
        mode = AppContext.PICK_MODE_PLANE_LOCK if value == "Plane Lock" else AppContext.PICK_MODE_SURFACE
        self._context.set_pick_mode(mode)
        self.pick_mode_changed.emit(mode)

    def _on_edit_plane_changed(self, value: str) -> None:
        if self._context is None:
            return
        self._context.set_edit_plane(value.lower())
        self.edit_plane_changed.emit(self._context.edit_plane)

    def _on_fill_connectivity_changed(self, value: str) -> None:
        if self._context is None:
            return
        mode = (
            AppContext.FILL_CONNECTIVITY_VOLUME
            if value == "3D"
            else AppContext.FILL_CONNECTIVITY_PLANE
        )
        self._context.set_fill_connectivity(mode)
        self.fill_connectivity_changed.emit(mode)

    def _on_selection_mode_toggled(self, state: int) -> None:
        if self._context is None:
            return
        enabled = state == Qt.Checked
        self._context.set_voxel_selection_mode(enabled)
        if not enabled:
            self._context.clear_selected_voxels()
        self.selection_mode_changed.emit(enabled)

    def _on_duplicate_selected_clicked(self) -> None:
        if self._context is None:
            return
        self.duplicate_selected_requested.emit(
            int(self.duplicate_offset_x_spin.value()),
            int(self.duplicate_offset_y_spin.value()),
            int(self.duplicate_offset_z_spin.value()),
        )

    def set_tool_shape(self, shape: str) -> None:
        if shape == AppContext.TOOL_SHAPE_BRUSH:
            self.brush_shape_radio.setChecked(True)
            return
        if shape == AppContext.TOOL_SHAPE_BOX:
            self.box_shape_radio.setChecked(True)
            return
        if shape == AppContext.TOOL_SHAPE_LINE:
            self.line_shape_radio.setChecked(True)
            return
        if shape == AppContext.TOOL_SHAPE_FILL:
            self.fill_shape_radio.setChecked(True)
            return

    def set_tool_mode(self, mode: str) -> None:
        if mode == AppContext.TOOL_MODE_PAINT:
            self.paint_radio.setChecked(True)
            return
        if mode == AppContext.TOOL_MODE_ERASE:
            self.erase_radio.setChecked(True)

    def _build_hint_text(self) -> str:
        if self._context is None:
            return ""

        shape = self._context.voxel_tool_shape
        mode = self._context.voxel_tool_mode
        tool_hint = ""
        if shape == AppContext.TOOL_SHAPE_BRUSH:
            brush_kind = self._context.brush_shape.capitalize()
            pick_label = "Plane Lock" if self._context.pick_mode == AppContext.PICK_MODE_PLANE_LOCK else "Surface"
            tool_hint = (
                "Brush: click-drag to paint continuously. "
                f"Profile: {brush_kind} size {self._context.brush_size}. "
                f"Pick: {pick_label}. Hold Shift for temporary erase."
            )
        elif shape == AppContext.TOOL_SHAPE_BOX:
            tool_hint = "Box: click-drag to fill/erase a rectangle on the edit plane."
        elif shape == AppContext.TOOL_SHAPE_LINE:
            tool_hint = "Line: click-drag to draw a straight voxel line on the edit plane."
        else:
            fill_mode = "3D" if self._context.fill_connectivity == AppContext.FILL_CONNECTIVITY_VOLUME else "Plane"
            tool_hint = f"Fill: click a connected region ({fill_mode}). Large fills are safety-limited."

        mode_hint = f"Current mode: {mode.upper()} | Shortcuts: B/X/L/F tools, P/E mode, Shift+F frame."
        plane_hint = f"Edit plane: {self._context.edit_plane.upper()}."
        first_use = (
            "First-use flow: 1) Debug -> Create Test Voxels (Cross) 2) View -> Frame Voxels "
            "3) Paint/Edit 4) File -> Export OBJ/glTF/VOX."
        )
        return f"{tool_hint}\n{mode_hint} {plane_hint}\n{first_use}"
