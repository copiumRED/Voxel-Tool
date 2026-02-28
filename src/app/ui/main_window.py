from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDockWidget, QFileDialog, QMainWindow

from app.app_context import AppContext
from core.io.project_io import load_project, save_project
from core.project import Project, utc_now_iso
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
        self._build_file_menu()
        self.statusBar().showMessage("Ready")

    def _add_dock(self, title: str, widget, area: Qt.DockWidgetArea) -> None:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"{title.lower()}_dock")
        dock.setWidget(widget)
        self.addDockWidget(area, dock)

    def _build_file_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        new_action = QAction("New Project", self)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        save_action = QAction("Save Project", self)
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Project As", self)
        save_as_action.triggered.connect(self._on_save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _on_new_project(self) -> None:
        self.context.current_project = Project(name="Untitled")
        self.context.current_path = None
        self.statusBar().showMessage("New project created: Untitled", 4000)

    def _on_open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "Project JSON (*.json);;All Files (*)",
        )
        if not path:
            return
        project = load_project(path)
        self.context.current_project = project
        self.context.current_path = path
        self.statusBar().showMessage(f"Loaded: {path}", 5000)

    def _on_save_project(self) -> None:
        if not self.context.current_path:
            self._on_save_project_as()
            return
        self._save_to_path(self.context.current_path)

    def _on_save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            "",
            "Project JSON (*.json);;All Files (*)",
        )
        if not path:
            return
        self.context.current_path = path
        self._save_to_path(path)

    def _save_to_path(self, path: str) -> None:
        self.context.current_project.modified_utc = utc_now_iso()
        save_project(self.context.current_project, path)
        self.statusBar().showMessage(f"Saved: {path}", 5000)

