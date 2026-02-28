from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QLabel, QRadioButton, QVBoxLayout, QWidget

from app.app_context import AppContext


class ToolsPanel(QWidget):
    tool_mode_changed = Signal(str)
    tool_shape_changed = Signal(str)
    mirror_changed = Signal(str, bool)

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
        self.mirror_x_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("x", checked))
        self.mirror_y_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("y", checked))
        self.mirror_z_checkbox.toggled.connect(lambda checked: self._on_mirror_toggled("z", checked))
        layout.addWidget(self.mirror_x_checkbox)
        layout.addWidget(self.mirror_y_checkbox)
        layout.addWidget(self.mirror_z_checkbox)
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
        self.paint_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_PAINT)
        self.erase_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_ERASE)
        self.brush_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BRUSH)
        self.box_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BOX)
        self.line_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_LINE)
        self.fill_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_FILL)
        self.mirror_x_checkbox.setChecked(self._context.mirror_x_enabled)
        self.mirror_y_checkbox.setChecked(self._context.mirror_y_enabled)
        self.mirror_z_checkbox.setChecked(self._context.mirror_z_enabled)
        self.paint_radio.blockSignals(False)
        self.erase_radio.blockSignals(False)
        self.brush_shape_radio.blockSignals(False)
        self.box_shape_radio.blockSignals(False)
        self.line_shape_radio.blockSignals(False)
        self.fill_shape_radio.blockSignals(False)
        self.mirror_x_checkbox.blockSignals(False)
        self.mirror_y_checkbox.blockSignals(False)
        self.mirror_z_checkbox.blockSignals(False)

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

    def set_tool_mode(self, mode: str) -> None:
        if mode == AppContext.TOOL_MODE_PAINT:
            self.paint_radio.setChecked(True)
            return
        if mode == AppContext.TOOL_MODE_ERASE:
            self.erase_radio.setChecked(True)
