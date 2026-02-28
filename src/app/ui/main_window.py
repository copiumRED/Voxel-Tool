from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QMainWindow

from app.app_context import AppContext
from app.ui.panels.inspector_panel import InspectorPanel
from app.ui.panels.palette_panel import PalettePanel
from app.ui.panels.stats_panel import StatsPanel
from app.ui.panels.tools_panel import ToolsPanel
from app.viewport.gl_widget import GLViewportWidget


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.setWindowTitle("Voxel Tool - Phase 0")
        self.resize(1280, 720)

        self.setCentralWidget(GLViewportWidget(self))
        self._add_dock("Tools", ToolsPanel(self), Qt.LeftDockWidgetArea)
        self._add_dock("Inspector", InspectorPanel(self), Qt.RightDockWidgetArea)
        self._add_dock("Palette", PalettePanel(self), Qt.RightDockWidgetArea)
        self._add_dock("Stats", StatsPanel(self), Qt.BottomDockWidgetArea)

    def _add_dock(self, title: str, widget, area: Qt.DockWidgetArea) -> None:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"{title.lower()}_dock")
        dock.setWidget(widget)
        self.addDockWidget(area, dock)

