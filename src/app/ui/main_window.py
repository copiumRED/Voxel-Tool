from __future__ import annotations

import logging
import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QDockWidget, QFileDialog, QInputDialog, QMainWindow, QMessageBox

from app.app_context import AppContext
from app.settings import get_settings
from core.commands.demo_commands import (
    ClearVoxelsCommand,
    CreateTestVoxelsCommand,
    PaintVoxelCommand,
    RenameProjectCommand,
)
from core.export.obj_exporter import export_voxels_to_obj
from core.export.gltf_exporter import export_voxels_to_gltf
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
        self.viewport.voxel_edit_applied.connect(self._on_viewport_voxel_edit_applied)
        self.viewport.viewport_ready.connect(self._on_viewport_ready)
        self.viewport.viewport_error.connect(self._on_viewport_error)
        self.setCentralWidget(self.viewport)
        self.tools_panel = ToolsPanel(self)
        self.tools_panel.set_context(self.context)
        self.tools_panel.tool_mode_changed.connect(self._on_tool_mode_changed)
        self.tools_panel.tool_shape_changed.connect(self._on_tool_shape_changed)
        self.tools_panel.mirror_changed.connect(self._on_mirror_changed)
        self.tools_dock = self._add_dock("Tools", self.tools_panel, Qt.LeftDockWidgetArea)
        self.inspector_panel = InspectorPanel(self)
        self.inspector_panel.set_context(self.context)
        self.inspector_panel.part_selection_changed.connect(self._on_part_selection_changed)
        self.inspector_dock = self._add_dock("Inspector", self.inspector_panel, Qt.RightDockWidgetArea)
        self.palette_panel = PalettePanel(self)
        self.palette_panel.set_context(self.context)
        self.palette_panel.active_color_changed.connect(self._on_active_color_changed)
        self.palette_dock = self._add_dock("Palette", self.palette_panel, Qt.RightDockWidgetArea)
        self.stats_panel = StatsPanel(self)
        self.stats_dock = self._add_dock("Stats", self.stats_panel, Qt.BottomDockWidgetArea)
        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_voxels_menu()
        self._build_debug_menu()
        self.statusBar().showMessage("Ready")
        self._restore_layout_settings()
        self._refresh_ui_state()

    def _add_dock(self, title: str, widget, area: Qt.DockWidgetArea) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(f"{title.lower()}_dock")
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        return dock

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

        export_obj_action = QAction("Export OBJ", self)
        export_obj_action.triggered.connect(self._on_export_obj)
        file_menu.addAction(export_obj_action)

        export_gltf_action = QAction("Export glTF", self)
        export_gltf_action.triggered.connect(self._on_export_gltf)
        file_menu.addAction(export_gltf_action)

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

    def _build_view_menu(self) -> None:
        view_menu = self.menuBar().addMenu("&View")

        reset_camera_action = QAction("Reset Camera", self)
        reset_camera_action.triggered.connect(self._on_reset_camera)
        view_menu.addAction(reset_camera_action)

        frame_voxels_action = QAction("Frame Voxels", self)
        frame_voxels_action.triggered.connect(self._on_frame_voxels)
        view_menu.addAction(frame_voxels_action)

        view_menu.addSeparator()

        debug_overlay_action = QAction("Toggle Debug Overlay", self)
        debug_overlay_action.setCheckable(True)
        debug_overlay_action.setChecked(self.viewport.debug_overlay_enabled)
        debug_overlay_action.toggled.connect(self._on_toggle_debug_overlay)
        view_menu.addAction(debug_overlay_action)

        view_menu.addSeparator()

        reset_layout_action = QAction("Reset Layout", self)
        reset_layout_action.triggered.connect(self._on_reset_layout)
        view_menu.addAction(reset_layout_action)

    def _build_voxels_menu(self) -> None:
        voxels_menu = self.menuBar().addMenu("&Voxels")

        add_voxel_action = QAction("Demo: Add Random Voxel", self)
        add_voxel_action.triggered.connect(self._on_demo_add_random_voxel)
        voxels_menu.addAction(add_voxel_action)

        clear_voxels_action = QAction("Demo: Clear Voxels", self)
        clear_voxels_action.triggered.connect(self._on_demo_clear_voxels)
        voxels_menu.addAction(clear_voxels_action)

    def _build_debug_menu(self) -> None:
        debug_menu = self.menuBar().addMenu("&Debug")

        create_test_voxels_action = QAction("Create Test Voxels (Cross)", self)
        create_test_voxels_action.triggered.connect(self._on_create_test_voxels)
        debug_menu.addAction(create_test_voxels_action)

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

    def _on_export_obj(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export OBJ",
            "",
            "OBJ (*.obj);;All Files (*)",
        )
        if not path:
            return
        export_voxels_to_obj(self.context.current_project.voxels, self.context.palette, path)
        voxel_count = self.context.current_project.voxels.count()
        if voxel_count == 0:
            self.statusBar().showMessage(f"No voxels to export | Exported OBJ: {path}", 5000)
            return
        self.statusBar().showMessage(f"Exported OBJ: {path} | Voxels: {voxel_count}", 5000)

    def _on_export_gltf(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export glTF",
            "",
            "glTF (*.gltf);;All Files (*)",
        )
        if not path:
            return
        stats = export_voxels_to_gltf(self.context.current_project.voxels, path)
        if stats.triangle_count == 0:
            self.statusBar().showMessage(f"No voxels to export | Exported glTF: {path}", 5000)
            return
        self.statusBar().showMessage(
            f"Exported glTF: {path} | Vertices: {stats.vertex_count} | Triangles: {stats.triangle_count}",
            5000,
        )

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
        color_index = self.context.active_color_index
        self.context.command_stack.do(PaintVoxelCommand(x, y, z, color_index), self.context)
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
        self.palette_panel.refresh()
        self.inspector_panel.refresh()
        self.tools_panel.refresh()
        self.viewport.update()
        if self.undo_action is not None:
            self.undo_action.setEnabled(self.context.command_stack.can_undo)
        if self.redo_action is not None:
            self.redo_action.setEnabled(self.context.command_stack.can_redo)

    def _show_voxel_status(self, message: str) -> None:
        count = self.context.current_project.voxels.count()
        active = self.context.active_color_index
        part_name = self.context.active_part.name
        mode = self.context.voxel_tool_mode
        shape = self.context.voxel_tool_shape
        mirror_axes = "".join(
            axis
            for axis, enabled in (
                ("X", self.context.mirror_x_enabled),
                ("Y", self.context.mirror_y_enabled),
                ("Z", self.context.mirror_z_enabled),
            )
            if enabled
        ) or "-"
        self.statusBar().showMessage(
            f"{message} | Part: {part_name} | Voxels: {count} | Active Color: {active} | Tool: {shape}/{mode} | Mirror: {mirror_axes}",
            5000,
        )

    def _on_active_color_changed(self, index: int) -> None:
        self._show_voxel_status(f"Active Color: {index}")
        self._refresh_ui_state()

    def _on_toggle_debug_overlay(self, enabled: bool) -> None:
        self.viewport.debug_overlay_enabled = enabled
        self.viewport.update()

    def _on_reset_camera(self) -> None:
        self.viewport.reset_camera()

    def _on_frame_voxels(self) -> None:
        self.viewport.frame_to_voxels()

    def _on_viewport_voxel_edit_applied(self, message: str) -> None:
        self._show_voxel_status(message)
        self._refresh_ui_state()

    def _on_part_selection_changed(self, part_id: str) -> None:
        self._show_voxel_status(f"Active part: {self.context.active_part.name} ({part_id})")
        self.viewport.frame_to_voxels()
        self._refresh_ui_state()

    def _on_tool_mode_changed(self, mode: str) -> None:
        self._show_voxel_status(f"Tool mode: {mode}")
        self._refresh_ui_state()

    def _on_tool_shape_changed(self, shape: str) -> None:
        self._show_voxel_status(f"Tool shape: {shape}")
        self._refresh_ui_state()

    def _on_mirror_changed(self, axis: str, enabled: bool) -> None:
        state = "on" if enabled else "off"
        self._show_voxel_status(f"Mirror {axis.upper()}: {state}")
        self._refresh_ui_state()

    def _on_create_test_voxels(self) -> None:
        center_color = self.context.active_color_index
        arm_color = (center_color + 3) % len(self.context.palette)
        self.context.command_stack.do(CreateTestVoxelsCommand(center_color, arm_color), self.context)
        self.viewport.frame_to_voxels()
        self._show_voxel_status("Test voxels created")
        self._refresh_ui_state()

    def _on_reset_layout(self) -> None:
        settings = get_settings()
        settings.remove("main_window/geometry")
        settings.remove("main_window/state")
        self.resize(1280, 720)
        self._apply_default_layout()
        settings.setValue("main_window/geometry", self.saveGeometry())
        settings.setValue("main_window/state", self.saveState())

    def _on_viewport_ready(self, gl_info: str) -> None:
        logging.getLogger("voxel_tool").info("Viewport ready | OpenGL: %s", gl_info)
        self.statusBar().showMessage(f"Viewport ready | OpenGL: {gl_info}", 8000)

    def _on_viewport_error(self, message: str) -> None:
        QMessageBox.critical(
            self,
            "OpenGL Error",
            "Failed to initialize OpenGL context.\n"
            "Please update your GPU drivers and ensure OpenGL is supported.\n\n"
            f"Details: {message}",
        )

    def _restore_layout_settings(self) -> None:
        settings = get_settings()
        geometry = settings.value("main_window/geometry")
        state = settings.value("main_window/state")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)
        else:
            self._apply_default_layout()

    def _apply_default_layout(self) -> None:
        self.tools_dock.show()
        self.inspector_dock.show()
        self.palette_dock.show()
        self.stats_dock.show()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tools_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.palette_dock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.stats_dock)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = get_settings()
        settings.setValue("main_window/geometry", self.saveGeometry())
        settings.setValue("main_window/state", self.saveState())
        super().closeEvent(event)

