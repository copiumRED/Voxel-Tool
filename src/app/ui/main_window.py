from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QDockWidget, QFileDialog, QInputDialog, QMainWindow

from app.app_context import AppContext
from app.settings import get_settings
from core.commands.demo_commands import AddVoxelCommand, ClearVoxelsCommand, RenameProjectCommand
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
        self.resize(1280, 720)
        self.undo_action: QAction | None = None
        self.redo_action: QAction | None = None

        self.viewport = GLViewportWidget(self)
        self.viewport.set_context(self.context)
        self.setCentralWidget(self.viewport)
        self._add_dock("Tools", ToolsPanel(self), Qt.LeftDockWidgetArea)
        self._add_dock("Inspector", InspectorPanel(self), Qt.RightDockWidgetArea)
        self._add_dock("Palette", PalettePanel(self), Qt.RightDockWidgetArea)
        self.stats_panel = StatsPanel(self)
        self._add_dock("Stats", self.stats_panel, Qt.BottomDockWidgetArea)
        self._build_file_menu()
        self._build_edit_menu()
        self._build_voxels_menu()
        self.statusBar().showMessage("Ready")
        self._restore_layout_settings()
        self._refresh_ui_state()

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

        demo_rename_action = QAction("Demo: Rename Project", self)
        demo_rename_action.triggered.connect(self._on_demo_rename_project)
        file_menu.addAction(demo_rename_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _build_edit_menu(self) -> None:
        edit_menu = self.menuBar().addMenu("&Edit")

        self.undo_action = QAction("Undo", self)
        self.undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("Redo", self)
        self.redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(self.redo_action)

    def _build_voxels_menu(self) -> None:
        voxels_menu = self.menuBar().addMenu("&Voxels")

        add_voxel_action = QAction("Demo: Add Random Voxel", self)
        add_voxel_action.triggered.connect(self._on_demo_add_random_voxel)
        voxels_menu.addAction(add_voxel_action)

        clear_voxels_action = QAction("Demo: Clear Voxels", self)
        clear_voxels_action.triggered.connect(self._on_demo_clear_voxels)
        voxels_menu.addAction(clear_voxels_action)

    def _on_new_project(self) -> None:
        self.context.current_project = Project(name="Untitled")
        self.context.current_path = None
        self.context.command_stack.clear()
        self.viewport.frame_to_voxels()
        self._show_voxel_status("New project created: Untitled")
        self._refresh_ui_state()

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
        self.context.command_stack.clear()
        self.viewport.frame_to_voxels()
        self._show_voxel_status(f"Loaded: {path}")
        self._refresh_ui_state()

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

    def _on_demo_rename_project(self) -> None:
        text, ok = QInputDialog.getText(
            self,
            "Rename Project",
            "New project name:",
            text=self.context.current_project.name,
        )
        new_name = text.strip()
        if not ok or not new_name:
            return

        self.context.command_stack.do(RenameProjectCommand(new_name), self.context)
        self._show_voxel_status(f"Renamed project: {new_name}")
        self._refresh_ui_state()

    def _on_undo(self) -> None:
        self.context.command_stack.undo(self.context)
        self._show_voxel_status("Undo")
        self._refresh_ui_state()

    def _on_redo(self) -> None:
        self.context.command_stack.redo(self.context)
        self._show_voxel_status("Redo")
        self._refresh_ui_state()

    def _on_demo_add_random_voxel(self) -> None:
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
        z = random.randint(-5, 5)
        color_index = random.randint(0, 7)
        self.context.command_stack.do(AddVoxelCommand(x, y, z, color_index), self.context)
        self._show_voxel_status(f"Added voxel: ({x}, {y}, {z}) color {color_index}")
        self._refresh_ui_state()

    def _on_demo_clear_voxels(self) -> None:
        self.context.command_stack.do(ClearVoxelsCommand(), self.context)
        self.viewport.frame_to_voxels()
        self._show_voxel_status("Cleared voxels")
        self._refresh_ui_state()

    def _refresh_ui_state(self) -> None:
        self.setWindowTitle(f"Voxel Tool - Phase 0 - {self.context.current_project.name}")
        self.stats_panel.set_voxel_count(self.context.current_project.voxels.count())
        self.viewport.update()
        if self.undo_action is not None:
            self.undo_action.setEnabled(self.context.command_stack.can_undo)
        if self.redo_action is not None:
            self.redo_action.setEnabled(self.context.command_stack.can_redo)

    def _show_voxel_status(self, message: str) -> None:
        count = self.context.current_project.voxels.count()
        self.statusBar().showMessage(f"{message} | Voxels: {count}", 5000)

    def _restore_layout_settings(self) -> None:
        settings = get_settings()
        geometry = settings.value("main_window/geometry")
        state = settings.value("main_window/state")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = get_settings()
        settings.setValue("main_window/geometry", self.saveGeometry())
        settings.setValue("main_window/state", self.saveState())
        super().closeEvent(event)

