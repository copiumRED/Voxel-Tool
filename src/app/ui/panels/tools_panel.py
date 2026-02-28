from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QLabel, QRadioButton, QVBoxLayout, QWidget

from app.app_context import AppContext


class ToolsPanel(QWidget):
    tool_mode_changed = Signal(str)
    tool_shape_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._context: AppContext | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Plane Tool"))

        self.brush_shape_radio = QRadioButton("Brush", self)
        self.box_shape_radio = QRadioButton("Box", self)
        self.brush_shape_radio.setChecked(True)
        self.brush_shape_radio.toggled.connect(self._on_shape_toggled)
        self.box_shape_radio.toggled.connect(self._on_shape_toggled)

        layout.addWidget(self.brush_shape_radio)
        layout.addWidget(self.box_shape_radio)
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
        self.paint_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_PAINT)
        self.erase_radio.setChecked(self._context.voxel_tool_mode == AppContext.TOOL_MODE_ERASE)
        self.brush_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BRUSH)
        self.box_shape_radio.setChecked(self._context.voxel_tool_shape == AppContext.TOOL_SHAPE_BOX)
        self.paint_radio.blockSignals(False)
        self.erase_radio.blockSignals(False)
        self.brush_shape_radio.blockSignals(False)
        self.box_shape_radio.blockSignals(False)

    def _on_mode_toggled(self, checked: bool) -> None:
        if not checked or self._context is None:
            return
        mode = AppContext.TOOL_MODE_PAINT if self.paint_radio.isChecked() else AppContext.TOOL_MODE_ERASE
        self._context.set_voxel_tool_mode(mode)
        self.tool_mode_changed.emit(mode)

    def _on_shape_toggled(self, checked: bool) -> None:
        if not checked or self._context is None:
            return
        shape = AppContext.TOOL_SHAPE_BRUSH if self.brush_shape_radio.isChecked() else AppContext.TOOL_SHAPE_BOX
        self._context.set_voxel_tool_shape(shape)
        self.tool_shape_changed.emit(shape)
