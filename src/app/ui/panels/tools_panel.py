from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
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
        is_brush = self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BRUSH
        self.brush_size_spin.setEnabled(is_brush)
        self.brush_shape_combo.setEnabled(is_brush)
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
            tool_hint = (
                "Brush: click-drag to paint continuously. "
                f"Profile: {brush_kind} size {self._context.brush_size}. "
                "Hold Shift for temporary erase."
            )
        elif shape == AppContext.TOOL_SHAPE_BOX:
            tool_hint = "Box: click-drag to fill/erase a rectangle on the edit plane."
        elif shape == AppContext.TOOL_SHAPE_LINE:
            tool_hint = "Line: click-drag to draw a straight voxel line on the edit plane."
        else:
            tool_hint = "Fill: click a connected region. Large fills are safety-limited."

        mode_hint = f"Current mode: {mode.upper()} | Shortcuts: B/X/L/F tools, P/E mode, Shift+F frame."
        first_use = (
            "First-use flow: 1) Debug -> Create Test Voxels (Cross) 2) View -> Frame Voxels "
            "3) Paint/Edit 4) File -> Export OBJ/glTF/VOX."
        )
        return f"{tool_hint}\n{mode_hint}\n{first_use}"
