from __future__ import annotations

import logging
import os
import random
import time
from dataclasses import dataclass

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

from app.app_context import AppContext
from app.settings import get_settings
from core.commands.demo_commands import (
    ClearVoxelsCommand,
    CreateTestVoxelsCommand,
    PaintVoxelCommand,
    RenameProjectCommand,
)
from core.analysis.stats import compute_scene_stats
from core.export.obj_exporter import ObjExportOptions, export_voxels_to_obj
from core.export.gltf_exporter import export_voxels_to_gltf
from core.export.vox_exporter import export_voxels_to_vox
from core.io.project_io import load_project, save_project
from core.io.vox_io import load_vox_models_with_warnings
from core.io.recovery_io import (
    clear_recovery_snapshot,
    has_recovery_snapshot,
    load_recovery_snapshot,
    save_recovery_snapshot,
    write_recovery_diagnostic,
)
from core.meshing.solidify import rebuild_part_mesh
from core.project import Project, utc_now_iso
from app.ui.panels.inspector_panel import InspectorPanel
from app.ui.panels.palette_panel import PalettePanel
from app.ui.panels.stats_panel import StatsPanel
from app.ui.panels.tools_panel import ToolsPanel
from app.viewport.gl_widget import GLViewportWidget

AUTOSAVE_DEBOUNCE_MS = 5000


@dataclass(slots=True)
class _ExportSessionOptions:
    obj_use_greedy_mesh: bool = True
    obj_triangulate: bool = False
    obj_pivot_mode: str = "none"
    obj_multi_material: bool = False
    scale_preset: str = "Unity (1m)"


class _ExportOptionsDialog(QDialog):
    def __init__(self, parent: QMainWindow, format_name: str, options: _ExportSessionOptions) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Export Options ({format_name})")
        self._format_name = format_name
        self._options = options

        layout = QFormLayout(self)
        self.obj_greedy_checkbox = QCheckBox("Use Greedy Mesh", self)
        self.obj_greedy_checkbox.setChecked(options.obj_use_greedy_mesh)
        self.obj_triangulate_checkbox = QCheckBox("Triangulate Faces", self)
        self.obj_triangulate_checkbox.setChecked(options.obj_triangulate)
        self.obj_pivot_combo = QComboBox(self)
        self.obj_pivot_combo.addItems(["None", "Center", "Bottom"])
        self.obj_pivot_combo.setCurrentText(options.obj_pivot_mode.capitalize())
        self.obj_multi_material_checkbox = QCheckBox("Split Materials By Color", self)
        self.obj_multi_material_checkbox.setChecked(options.obj_multi_material)
        self.scale_preset_combo = QComboBox(self)
        self.scale_preset_combo.addItems(["Unity (1m)", "Unreal (1cm)", "Custom (placeholder)"])
        self.scale_preset_combo.setCurrentText(options.scale_preset)
        capabilities = _export_dialog_capabilities(format_name)

        if capabilities["obj_controls"]:
            layout.addRow(self.obj_greedy_checkbox)
            layout.addRow(self.obj_triangulate_checkbox)
            layout.addRow("Pivot Mode", self.obj_pivot_combo)
            layout.addRow(self.obj_multi_material_checkbox)
        if capabilities["scale_preset"]:
            layout.addRow("Scale Preset", self.scale_preset_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def to_options(self) -> _ExportSessionOptions:
        next_options = _ExportSessionOptions(
            obj_use_greedy_mesh=self._options.obj_use_greedy_mesh,
            obj_triangulate=self._options.obj_triangulate,
            obj_pivot_mode=self._options.obj_pivot_mode,
            obj_multi_material=self._options.obj_multi_material,
            scale_preset=self._options.scale_preset,
        )
        capabilities = _export_dialog_capabilities(self._format_name)
        if capabilities["obj_controls"]:
            next_options.obj_use_greedy_mesh = self.obj_greedy_checkbox.isChecked()
            next_options.obj_triangulate = self.obj_triangulate_checkbox.isChecked()
            next_options.obj_pivot_mode = self.obj_pivot_combo.currentText().strip().lower()
            next_options.obj_multi_material = self.obj_multi_material_checkbox.isChecked()
        if capabilities["scale_preset"]:
            next_options.scale_preset = self.scale_preset_combo.currentText()
        return next_options


def _scale_factor_from_preset(preset: str) -> float:
    normalized = preset.strip().lower()
    if "unreal" in normalized:
        return 100.0
    return 1.0


def _export_dialog_capabilities(format_name: str) -> dict[str, bool]:
    normalized = format_name.strip().upper()
    return {
        "obj_controls": normalized == "OBJ",
        "scale_preset": normalized in {"OBJ", "GLTF"},
    }


def _edit_plane_for_view_preset(preset: str) -> str:
    key = preset.strip().lower()
    if key in {"top", "bottom"}:
        return AppContext.EDIT_PLANE_XZ
    if key in {"left", "right"}:
        return AppContext.EDIT_PLANE_YZ
    return AppContext.EDIT_PLANE_XY


def _next_brush_size(current: int, *, min_size: int = 1, max_size: int = 3) -> int:
    current_value = int(current)
    if current_value < min_size or current_value > max_size:
        return min_size
    return min_size + ((current_value - min_size + 1) % (max_size - min_size + 1))


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.resize(1280, 720)
        self.undo_action: QAction | None = None
        self.redo_action: QAction | None = None
        self._shortcuts: list[QShortcut] = []
        self._export_options = _ExportSessionOptions()
        self._last_frame_ms = 0.0
        self._last_rebuild_ms = 0.0
        self._last_scene_triangles = 0
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(60000)
        self._autosave_timer.timeout.connect(self._on_autosave_tick)
        self._autosave_debounce_timer = QTimer(self)
        self._autosave_debounce_timer.setSingleShot(True)
        self._autosave_debounce_timer.setInterval(AUTOSAVE_DEBOUNCE_MS)
        self._autosave_debounce_timer.timeout.connect(self._save_recovery_snapshot_now)

        self.viewport = GLViewportWidget(self)
        self.viewport.set_context(self.context)
        self.viewport.voxel_edit_applied.connect(self._on_viewport_voxel_edit_applied)
        self.viewport.viewport_ready.connect(self._on_viewport_ready)
        self.viewport.viewport_diagnostics.connect(self._on_viewport_diagnostics)
        self.viewport.viewport_error.connect(self._on_viewport_error)
        self.viewport.runtime_metrics.connect(self._on_runtime_metrics)
        self.setCentralWidget(self.viewport)
        self.tools_panel = ToolsPanel(self)
        self.tools_panel.set_context(self.context)
        self.tools_panel.tool_mode_changed.connect(self._on_tool_mode_changed)
        self.tools_panel.tool_shape_changed.connect(self._on_tool_shape_changed)
        self.tools_panel.mirror_changed.connect(self._on_mirror_changed)
        self.tools_panel.mirror_offset_changed.connect(self._on_mirror_offset_changed)
        self.tools_panel.brush_profile_changed.connect(self._on_brush_profile_changed)
        self.tools_panel.pick_mode_changed.connect(self._on_pick_mode_changed)
        self.tools_panel.edit_plane_changed.connect(self._on_edit_plane_changed)
        self.tools_panel.fill_connectivity_changed.connect(self._on_fill_connectivity_changed)
        self.tools_dock = self._add_dock("Tools", self.tools_panel, Qt.LeftDockWidgetArea)
        self.inspector_panel = InspectorPanel(self)
        self.inspector_panel.set_context(self.context)
        self.inspector_panel.part_selection_changed.connect(self._on_part_selection_changed)
        self.inspector_panel.part_status_message.connect(self._on_part_status_message)
        self.inspector_dock = self._add_dock("Inspector", self.inspector_panel, Qt.RightDockWidgetArea)
        self.palette_panel = PalettePanel(self)
        self.palette_panel.set_context(self.context)
        self.palette_panel.active_color_changed.connect(self._on_active_color_changed)
        self.palette_panel.palette_status_message.connect(self._on_palette_status_message)
        self.palette_dock = self._add_dock("Palette", self.palette_panel, Qt.RightDockWidgetArea)
        self.stats_panel = StatsPanel(self)
        self.stats_dock = self._add_dock("Stats", self.stats_panel, Qt.BottomDockWidgetArea)
        self._build_file_menu()
        self._build_edit_menu()
        self._build_view_menu()
        self._build_voxels_menu()
        self._build_debug_menu()
        self._setup_shortcuts()
        self.statusBar().showMessage("Viewport: INITIALIZING | Shader: unknown | OpenGL: unknown")
        self._restore_layout_settings()
        self._prompt_recovery_if_available()
        self._refresh_ui_state()
        self._autosave_timer.start()

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
        import_vox_action = QAction("Import VOX", self)
        import_vox_action.triggered.connect(self._on_import_vox)
        file_menu.addAction(import_vox_action)

        file_menu.addSeparator()

        export_obj_action = QAction("Export OBJ", self)
        export_obj_action.triggered.connect(self._on_export_obj)
        file_menu.addAction(export_obj_action)

        export_gltf_action = QAction("Export glTF", self)
        export_gltf_action.triggered.connect(self._on_export_gltf)
        file_menu.addAction(export_gltf_action)

        export_vox_action = QAction("Export VOX", self)
        export_vox_action.triggered.connect(self._on_export_vox)
        file_menu.addAction(export_vox_action)

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

        edit_menu.addSeparator()
        set_undo_depth_action = QAction("Set Undo Depth", self)
        set_undo_depth_action.triggered.connect(self._on_set_undo_depth)
        edit_menu.addAction(set_undo_depth_action)

        shortcut_help_action = QAction("Shortcut Help", self)
        shortcut_help_action.triggered.connect(self._on_show_shortcut_help)
        edit_menu.addAction(shortcut_help_action)

    def _build_view_menu(self) -> None:
        view_menu = self.menuBar().addMenu("&View")

        reset_camera_action = QAction("Reset Camera", self)
        reset_camera_action.setShortcut(QKeySequence("Shift+R"))
        reset_camera_action.triggered.connect(self._on_reset_camera)
        view_menu.addAction(reset_camera_action)

        frame_voxels_action = QAction("Frame Voxels", self)
        frame_voxels_action.setShortcut(QKeySequence("Shift+F"))
        frame_voxels_action.triggered.connect(self._on_frame_voxels)
        view_menu.addAction(frame_voxels_action)

        presets_menu = view_menu.addMenu("View Presets")
        preset_specs = (
            ("Top", "Ctrl+1", "top"),
            ("Front", "Ctrl+2", "front"),
            ("Left", "Ctrl+3", "left"),
            ("Right", "Ctrl+4", "right"),
            ("Back", "Ctrl+5", "back"),
            ("Bottom", "Ctrl+6", "bottom"),
        )
        for label, shortcut, preset in preset_specs:
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(lambda _checked=False, key=preset: self._on_view_preset(key))
            presets_menu.addAction(action)

        view_menu.addSeparator()
        toggle_grid_action = QAction("Show Grid", self)
        toggle_grid_action.setCheckable(True)
        toggle_grid_action.setChecked(self.context.grid_visible)
        toggle_grid_action.toggled.connect(self._on_toggle_grid_visible)
        view_menu.addAction(toggle_grid_action)

        grid_spacing_action = QAction("Set Grid Spacing", self)
        grid_spacing_action.triggered.connect(self._on_set_grid_spacing)
        view_menu.addAction(grid_spacing_action)

        camera_snap_action = QAction("Camera Snap", self)
        camera_snap_action.setCheckable(True)
        camera_snap_action.setChecked(self.context.camera_snap_enabled)
        camera_snap_action.toggled.connect(self._on_toggle_camera_snap)
        view_menu.addAction(camera_snap_action)

        camera_snap_angle_action = QAction("Set Camera Snap Degrees", self)
        camera_snap_angle_action.triggered.connect(self._on_set_camera_snap_degrees)
        view_menu.addAction(camera_snap_angle_action)
        orbit_sensitivity_action = QAction("Set Orbit Sensitivity", self)
        orbit_sensitivity_action.triggered.connect(lambda: self._on_set_camera_sensitivity("orbit"))
        view_menu.addAction(orbit_sensitivity_action)
        pan_sensitivity_action = QAction("Set Pan Sensitivity", self)
        pan_sensitivity_action.triggered.connect(lambda: self._on_set_camera_sensitivity("pan"))
        view_menu.addAction(pan_sensitivity_action)
        zoom_sensitivity_action = QAction("Set Zoom Sensitivity", self)
        zoom_sensitivity_action.triggered.connect(lambda: self._on_set_camera_sensitivity("zoom"))
        view_menu.addAction(zoom_sensitivity_action)
        orthographic_action = QAction("Orthographic Projection", self)
        orthographic_action.setCheckable(True)
        orthographic_action.setChecked(
            self.context.camera_projection == AppContext.CAMERA_PROJECTION_ORTHOGRAPHIC
        )
        orthographic_action.toggled.connect(self._on_toggle_orthographic_projection)
        view_menu.addAction(orthographic_action)
        navigation_menu = view_menu.addMenu("Navigation Profile")
        navigation_group = QActionGroup(self)
        navigation_group.setExclusive(True)
        profile_specs = (
            ("Classic", AppContext.NAV_PROFILE_CLASSIC),
            ("MMB Orbit", AppContext.NAV_PROFILE_MMB_ORBIT),
            ("Blender-Mix", AppContext.NAV_PROFILE_BLENDER_MIX),
        )
        for label, profile in profile_specs:
            profile_action = QAction(label, self)
            profile_action.setCheckable(True)
            profile_action.setChecked(self.context.navigation_profile == profile)
            profile_action.triggered.connect(
                lambda _checked=False, profile_value=profile: self._set_navigation_profile(profile_value)
            )
            navigation_group.addAction(profile_action)
            navigation_menu.addAction(profile_action)

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

        solidify_action = QAction("Solidify/Rebuild Mesh", self)
        solidify_action.triggered.connect(self._on_solidify_rebuild_mesh)
        voxels_menu.addAction(solidify_action)
        voxels_menu.addSeparator()

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

    def _setup_shortcuts(self) -> None:
        self._register_shortcut("B", lambda: self._set_tool_shape(AppContext.TOOL_SHAPE_BRUSH))
        self._register_shortcut("X", lambda: self._set_tool_shape(AppContext.TOOL_SHAPE_BOX))
        self._register_shortcut("L", lambda: self._set_tool_shape(AppContext.TOOL_SHAPE_LINE))
        self._register_shortcut("F", lambda: self._set_tool_shape(AppContext.TOOL_SHAPE_FILL))
        self._register_shortcut("P", lambda: self._set_tool_mode(AppContext.TOOL_MODE_PAINT))
        self._register_shortcut("E", lambda: self._set_tool_mode(AppContext.TOOL_MODE_ERASE))
        self._register_shortcut("1", lambda: self._set_active_palette_slot(0))
        self._register_shortcut("2", lambda: self._set_active_palette_slot(1))
        self._register_shortcut("3", lambda: self._set_active_palette_slot(2))
        self._register_shortcut("4", lambda: self._set_active_palette_slot(3))
        self._register_shortcut("5", lambda: self._set_active_palette_slot(4))
        self._register_shortcut("6", lambda: self._set_active_palette_slot(5))
        self._register_shortcut("7", lambda: self._set_active_palette_slot(6))
        self._register_shortcut("8", lambda: self._set_active_palette_slot(7))
        self._register_shortcut("9", lambda: self._set_active_palette_slot(8))
        self._register_shortcut("0", lambda: self._set_active_palette_slot(9))
        self._register_shortcut("Shift+F", self._on_frame_voxels)
        self._register_shortcut("Shift+R", self._on_reset_camera)
        self._register_shortcut("]", self._cycle_brush_size)

    def _register_shortcut(self, sequence: str, callback) -> None:
        shortcut = QShortcut(QKeySequence(sequence), self)
        shortcut.activated.connect(callback)
        self._shortcuts.append(shortcut)

    def _set_tool_shape(self, shape: str) -> None:
        self.tools_panel.set_tool_shape(shape)

    def _set_tool_mode(self, mode: str) -> None:
        self.tools_panel.set_tool_mode(mode)

    def _set_active_palette_slot(self, index: int) -> None:
        if not self.context.palette:
            return
        slot = max(0, min(index, len(self.context.palette) - 1))
        self.context.active_color_index = slot
        self._show_voxel_status(f"Active Color: {slot}")
        self._refresh_ui_state()

    def _cycle_brush_size(self) -> None:
        next_size = _next_brush_size(self.context.brush_size)
        self.context.set_brush_size(next_size)
        self._show_voxel_status(f"Brush size: {next_size}")
        self._refresh_ui_state()

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
        try:
            project = load_project(path)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Open Project Failed",
                "Failed to open project file. The file may be invalid or corrupt.\n\n"
                f"Details: {exc}",
            )
            return
        self.context.current_project = project
        self.context.current_path = path
        self._apply_editor_state(project.editor_state)
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
        self.context.current_project.editor_state = self._capture_editor_state()
        save_project(self.context.current_project, path)
        self.statusBar().showMessage(f"Saved: {path}", 5000)

    def _on_export_obj(self) -> None:
        export_options = self._prompt_export_options("OBJ")
        if export_options is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export OBJ",
            "",
            "OBJ (*.obj);;All Files (*)",
        )
        if not path:
            return
        export_voxels_to_obj(
            self.context.current_project.voxels,
            self.context.palette,
            path,
            options=ObjExportOptions(
                use_greedy_mesh=export_options.obj_use_greedy_mesh,
                triangulate=export_options.obj_triangulate,
                scale_factor=_scale_factor_from_preset(export_options.scale_preset),
                pivot_mode=export_options.obj_pivot_mode,
                multi_material_by_color=export_options.obj_multi_material,
            ),
            mesh=(
                self.context.active_part.mesh_cache
                if self.context.active_part.dirty_bounds is None
                else None
            ),
        )
        voxel_count = self.context.current_project.voxels.count()
        if voxel_count == 0:
            self.statusBar().showMessage(
                f"No voxels to export | Exported OBJ: {path} | Scale: {export_options.scale_preset}",
                5000,
            )
            return
        self.statusBar().showMessage(
            (
                f"Exported OBJ: {path} | Voxels: {voxel_count} | "
                f"Greedy: {export_options.obj_use_greedy_mesh} | "
                f"Triangulate: {export_options.obj_triangulate} | "
                f"Pivot: {export_options.obj_pivot_mode} | Scale: {export_options.scale_preset}"
            ),
            5000,
        )

    def _on_import_vox(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import VOX",
            "",
            "VOX (*.vox);;All Files (*)",
        )
        if not path:
            return
        try:
            models, palette, warnings = load_vox_models_with_warnings(path)
        except Exception as exc:
            QMessageBox.warning(self, "Import VOX", f"Failed to import VOX file.\n\n{exc}")
            return

        scene = self.context.current_project.scene
        part_name = os.path.splitext(os.path.basename(path))[0] or "Imported VOX"
        imported_count = 0
        active_part_id: str | None = None
        for index, voxels in enumerate(models):
            name = part_name if len(models) == 1 else f"{part_name} #{index + 1}"
            imported_part = scene.add_part(name)
            imported_part.voxels = voxels
            if active_part_id is None:
                active_part_id = imported_part.part_id
            imported_count += 1
        if active_part_id is not None:
            scene.set_active_part(active_part_id)
        self.context.palette = palette
        self.context.active_color_index = max(
            0,
            min(self.context.active_color_index, len(self.context.palette) - 1),
        )
        self._show_voxel_status(f"Imported VOX: {path} ({imported_count} part(s))")
        if warnings:
            QMessageBox.information(
                self,
                "VOX Import Warnings",
                "Imported with unsupported chunk(s): " + ", ".join(warnings),
            )
        self._refresh_ui_state()

    def _on_export_gltf(self) -> None:
        export_options = self._prompt_export_options("glTF")
        if export_options is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export glTF",
            "",
            "glTF (*.gltf);;All Files (*)",
        )
        if not path:
            return
        stats = export_voxels_to_gltf(
            self.context.current_project.voxels,
            path,
            scale_factor=_scale_factor_from_preset(export_options.scale_preset),
            mesh=(
                self.context.active_part.mesh_cache
                if self.context.active_part.dirty_bounds is None
                else None
            ),
        )
        if stats.triangle_count == 0:
            self.statusBar().showMessage(
                f"No voxels to export | Exported glTF: {path} | Scale: {export_options.scale_preset}",
                5000,
            )
            return
        self.statusBar().showMessage(
            (
                f"Exported glTF: {path} | Vertices: {stats.vertex_count} | "
                f"Triangles: {stats.triangle_count} | Scale: {export_options.scale_preset}"
            ),
            5000,
        )

    def _on_export_vox(self) -> None:
        export_options = self._prompt_export_options("VOX")
        if export_options is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export VOX",
            "",
            "VOX (*.vox);;All Files (*)",
        )
        if not path:
            return
        stats = export_voxels_to_vox(self.context.current_project.voxels, self.context.palette, path)
        if stats.voxel_count == 0:
            self.statusBar().showMessage(
                f"No voxels to export | Exported VOX: {path}",
                5000,
            )
            return
        sx, sy, sz = stats.size
        self.statusBar().showMessage(
            (
                f"Exported VOX: {path} | Voxels: {stats.voxel_count} | Size: {sx}x{sy}x{sz}"
            ),
            5000,
        )

    def _prompt_export_options(self, format_name: str) -> _ExportSessionOptions | None:
        dialog = _ExportOptionsDialog(self, format_name, self._export_options)
        if dialog.exec() != QDialog.Accepted:
            return None
        self._export_options = dialog.to_options()
        return self._export_options

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

    def _on_solidify_rebuild_mesh(self) -> None:
        part = self.context.active_part
        start = time.perf_counter()
        mesh = rebuild_part_mesh(part, greedy=True)
        self._last_rebuild_ms = (time.perf_counter() - start) * 1000.0
        self._show_voxel_status(
            f"Solidified part: {part.name} | Faces: {mesh.face_count} | Vertices: {len(mesh.vertices)}"
        )
        self._refresh_ui_state()

    def _on_undo(self) -> None:
        self.context.command_stack.undo(self.context)
        self._show_voxel_status("Undo")
        self._refresh_ui_state()

    def _on_redo(self) -> None:
        self.context.command_stack.redo(self.context)
        self._show_voxel_status("Redo")
        self._refresh_ui_state()

    def _on_set_undo_depth(self) -> None:
        value, accepted = QInputDialog.getInt(
            self,
            "Undo Depth",
            "Maximum undo steps:",
            self.context.command_stack.max_undo_steps,
            1,
            5000,
            1,
        )
        if not accepted:
            return
        self.context.command_stack.set_max_undo_steps(value)
        self._show_voxel_status(f"Undo depth: {value}")
        self._refresh_ui_state()

    def _on_show_shortcut_help(self) -> None:
        QMessageBox.information(
            self,
            "Shortcut Help",
            "Tools: B/X/L/F\n"
            "Modes: P/E\n"
            "Palette: 1..0\n"
            "Camera: Shift+F frame, Shift+R reset\n"
            "Views: Ctrl+1..Ctrl+6",
        )

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
        scene_stats = compute_scene_stats(self.context.current_project)
        self.stats_panel.set_scene_stats(
            scene_stats,
            active_part_id=self.context.active_part_id,
            active_voxel_count=self.context.current_project.voxels.count(),
        )
        self._last_scene_triangles = scene_stats.triangles
        self.stats_panel.set_runtime_stats(
            frame_ms=self._last_frame_ms,
            rebuild_ms=self._last_rebuild_ms,
            scene_triangles=self._last_scene_triangles,
            scene_voxels=sum(part.voxels.count() for part in self.context.current_project.scene.parts.values()),
            active_part_voxels=self.context.current_project.voxels.count(),
        )
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
            (
                f"{message} | Part: {part_name} | Voxels: {count} | Active Color: {active} | "
                f"Tool: {shape}/{mode} | Brush: {self.context.brush_shape}{self.context.brush_size} | Mirror: {mirror_axes}"
            ),
            5000,
        )

    def _on_active_color_changed(self, index: int) -> None:
        self._show_voxel_status(f"Active Color: {index}")
        self._refresh_ui_state()

    def _on_palette_status_message(self, message: str) -> None:
        self._show_voxel_status(message)
        self._refresh_ui_state()

    def _on_toggle_debug_overlay(self, enabled: bool) -> None:
        self.viewport.debug_overlay_enabled = enabled
        self.viewport.update()

    def _on_reset_camera(self) -> None:
        self.viewport.reset_camera()

    def _on_frame_voxels(self) -> None:
        self.viewport.frame_to_voxels()

    def _on_view_preset(self, preset: str) -> None:
        self.viewport.set_view_preset(preset)
        next_plane = _edit_plane_for_view_preset(preset)
        self.context.set_edit_plane(next_plane)
        self._show_voxel_status(f"View preset: {preset} | Edit plane: {next_plane.upper()}")
        self._refresh_ui_state()

    def _on_toggle_grid_visible(self, enabled: bool) -> None:
        self.context.grid_visible = enabled
        self._show_voxel_status(f"Grid: {'on' if enabled else 'off'}")
        self.viewport.update()

    def _on_set_grid_spacing(self) -> None:
        value, accepted = QInputDialog.getInt(
            self,
            "Grid Spacing",
            "Grid spacing (voxels):",
            self.context.grid_spacing,
            1,
            10,
            1,
        )
        if not accepted:
            return
        self.context.grid_spacing = int(value)
        self._show_voxel_status(f"Grid spacing: {value}")
        self.viewport.update()

    def _on_toggle_camera_snap(self, enabled: bool) -> None:
        self.context.camera_snap_enabled = enabled
        self._show_voxel_status(f"Camera snap: {'on' if enabled else 'off'}")

    def _on_set_camera_snap_degrees(self) -> None:
        value, accepted = QInputDialog.getInt(
            self,
            "Camera Snap Degrees",
            "Snap degrees:",
            self.context.camera_snap_degrees,
            1,
            90,
            1,
        )
        if not accepted:
            return
        self.context.camera_snap_degrees = int(value)
        self._show_voxel_status(f"Camera snap degrees: {value}")

    def _on_set_camera_sensitivity(self, axis: str) -> None:
        axis_key = axis.strip().lower()
        current = 1.0
        if axis_key == "orbit":
            current = self.context.camera_orbit_sensitivity
        elif axis_key == "pan":
            current = self.context.camera_pan_sensitivity
        elif axis_key == "zoom":
            current = self.context.camera_zoom_sensitivity
        value, accepted = QInputDialog.getDouble(
            self,
            "Camera Sensitivity",
            f"{axis_key.title()} sensitivity:",
            float(current),
            0.1,
            3.0,
            2,
        )
        if not accepted:
            return
        self.context.set_camera_sensitivity(axis_key, value)
        self._show_voxel_status(f"{axis_key.title()} sensitivity: {value:.2f}")

    def _on_toggle_orthographic_projection(self, enabled: bool) -> None:
        projection = (
            AppContext.CAMERA_PROJECTION_ORTHOGRAPHIC
            if enabled
            else AppContext.CAMERA_PROJECTION_PERSPECTIVE
        )
        self.context.set_camera_projection(projection)
        self._show_voxel_status(f"Projection: {projection}")
        self.viewport.update()

    def _set_navigation_profile(self, profile: str) -> None:
        self.context.set_navigation_profile(profile)
        self._show_voxel_status(f"Navigation profile: {profile}")
        self.viewport.update()

    def _on_viewport_voxel_edit_applied(self, message: str) -> None:
        self._autosave_debounce_timer.start()
        self._show_voxel_status(message)
        self._refresh_ui_state()

    def _on_part_selection_changed(self, part_id: str) -> None:
        self._show_voxel_status(f"Active part: {self.context.active_part.name} ({part_id})")
        self.viewport.frame_to_voxels()
        self._refresh_ui_state()

    def _on_part_status_message(self, message: str) -> None:
        self._show_voxel_status(message)
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

    def _on_mirror_offset_changed(self, axis: str, offset: int) -> None:
        self._show_voxel_status(f"Mirror {axis.upper()} offset: {offset}")
        self._refresh_ui_state()

    def _on_brush_profile_changed(self, size: int, shape: str) -> None:
        self._show_voxel_status(f"Brush profile: {shape}{size}")
        self._refresh_ui_state()

    def _on_pick_mode_changed(self, mode: str) -> None:
        self._show_voxel_status(f"Pick mode: {mode}")
        self._refresh_ui_state()

    def _on_edit_plane_changed(self, plane: str) -> None:
        self._show_voxel_status(f"Edit plane: {plane.upper()}")
        self._refresh_ui_state()

    def _on_fill_connectivity_changed(self, mode: str) -> None:
        self._show_voxel_status(f"Fill connectivity: {mode}")
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

    def _on_viewport_diagnostics(self, message: str) -> None:
        self.statusBar().showMessage(message, 10000)

    def _on_runtime_metrics(self, frame_ms: float, active_voxels: int) -> None:
        del active_voxels
        self._last_frame_ms = frame_ms
        self.stats_panel.set_runtime_stats(
            frame_ms=self._last_frame_ms,
            rebuild_ms=self._last_rebuild_ms,
            scene_triangles=self._last_scene_triangles,
            scene_voxels=sum(part.voxels.count() for part in self.context.current_project.scene.parts.values()),
            active_part_voxels=self.context.current_project.voxels.count(),
        )

    def _on_viewport_error(self, message: str) -> None:
        QMessageBox.critical(
            self,
            "OpenGL Error",
            "Failed to initialize OpenGL context.\n"
            "Please update your GPU drivers and ensure OpenGL is supported.\n\n"
            f"Details: {message}",
        )

    def _capture_editor_state(self) -> dict[str, object]:
        return {
            "active_color_index": self.context.active_color_index,
            "voxel_tool_mode": self.context.voxel_tool_mode,
            "voxel_tool_shape": self.context.voxel_tool_shape,
            "brush_size": self.context.brush_size,
            "brush_shape": self.context.brush_shape,
            "pick_mode": self.context.pick_mode,
            "edit_plane": self.context.edit_plane,
            "fill_connectivity": self.context.fill_connectivity,
            "locked_palette_slots": sorted(self.context.locked_palette_slots),
            "grid_visible": self.context.grid_visible,
            "grid_spacing": self.context.grid_spacing,
            "camera_snap_enabled": self.context.camera_snap_enabled,
            "camera_snap_degrees": self.context.camera_snap_degrees,
            "camera_projection": self.context.camera_projection,
            "navigation_profile": self.context.navigation_profile,
            "camera_orbit_sensitivity": self.context.camera_orbit_sensitivity,
            "camera_pan_sensitivity": self.context.camera_pan_sensitivity,
            "camera_zoom_sensitivity": self.context.camera_zoom_sensitivity,
            "undo_depth": self.context.command_stack.max_undo_steps,
            "mirror_x_enabled": self.context.mirror_x_enabled,
            "mirror_y_enabled": self.context.mirror_y_enabled,
            "mirror_z_enabled": self.context.mirror_z_enabled,
            "mirror_x_offset": self.context.mirror_x_offset,
            "mirror_y_offset": self.context.mirror_y_offset,
            "mirror_z_offset": self.context.mirror_z_offset,
            "fill_max_cells": self.context.fill_max_cells,
        }

    def _apply_editor_state(self, state: dict[str, object]) -> None:
        if not isinstance(state, dict):
            return
        palette_size = max(1, len(self.context.palette))
        active_color = int(state.get("active_color_index", self.context.active_color_index))
        self.context.active_color_index = max(0, min(active_color, palette_size - 1))

        mode = str(state.get("voxel_tool_mode", self.context.voxel_tool_mode))
        shape = str(state.get("voxel_tool_shape", self.context.voxel_tool_shape))
        if mode in (AppContext.TOOL_MODE_PAINT, AppContext.TOOL_MODE_ERASE):
            self.context.voxel_tool_mode = mode
        if shape in (
            AppContext.TOOL_SHAPE_BRUSH,
            AppContext.TOOL_SHAPE_BOX,
            AppContext.TOOL_SHAPE_LINE,
            AppContext.TOOL_SHAPE_FILL,
        ):
            self.context.voxel_tool_shape = shape
        self.context.brush_size = max(1, min(3, int(state.get("brush_size", self.context.brush_size))))
        brush_shape = str(state.get("brush_shape", self.context.brush_shape)).strip().lower()
        self.context.brush_shape = brush_shape if brush_shape in {"cube", "sphere"} else "cube"
        pick_mode = str(state.get("pick_mode", self.context.pick_mode)).strip().lower()
        if pick_mode in (AppContext.PICK_MODE_SURFACE, AppContext.PICK_MODE_PLANE_LOCK):
            self.context.pick_mode = pick_mode
        edit_plane = str(state.get("edit_plane", self.context.edit_plane)).strip().lower()
        if edit_plane in (
            AppContext.EDIT_PLANE_XY,
            AppContext.EDIT_PLANE_YZ,
            AppContext.EDIT_PLANE_XZ,
        ):
            self.context.edit_plane = edit_plane
        fill_connectivity = str(
            state.get("fill_connectivity", self.context.fill_connectivity)
        ).strip().lower()
        if fill_connectivity in (
            AppContext.FILL_CONNECTIVITY_PLANE,
            AppContext.FILL_CONNECTIVITY_VOLUME,
        ):
            self.context.fill_connectivity = fill_connectivity
        raw_locked_slots = state.get("locked_palette_slots", [])
        next_locked_slots: set[int] = set()
        if isinstance(raw_locked_slots, list):
            for raw in raw_locked_slots:
                try:
                    slot = int(raw)
                except (TypeError, ValueError):
                    continue
                if 0 <= slot < len(self.context.palette):
                    next_locked_slots.add(slot)
        self.context.locked_palette_slots = next_locked_slots
        self.context.grid_visible = bool(state.get("grid_visible", self.context.grid_visible))
        self.context.grid_spacing = max(1, int(state.get("grid_spacing", self.context.grid_spacing)))
        self.context.camera_snap_enabled = bool(
            state.get("camera_snap_enabled", self.context.camera_snap_enabled)
        )
        self.context.camera_snap_degrees = max(
            1,
            int(state.get("camera_snap_degrees", self.context.camera_snap_degrees)),
        )
        projection = str(state.get("camera_projection", self.context.camera_projection)).strip().lower()
        if projection in (
            AppContext.CAMERA_PROJECTION_PERSPECTIVE,
            AppContext.CAMERA_PROJECTION_ORTHOGRAPHIC,
        ):
            self.context.camera_projection = projection
        navigation_profile = str(
            state.get("navigation_profile", self.context.navigation_profile)
        ).strip().lower()
        if navigation_profile in (
            AppContext.NAV_PROFILE_CLASSIC,
            AppContext.NAV_PROFILE_MMB_ORBIT,
            AppContext.NAV_PROFILE_BLENDER_MIX,
        ):
            self.context.navigation_profile = navigation_profile
        self.context.camera_orbit_sensitivity = max(
            0.1,
            min(3.0, float(state.get("camera_orbit_sensitivity", self.context.camera_orbit_sensitivity))),
        )
        self.context.camera_pan_sensitivity = max(
            0.1,
            min(3.0, float(state.get("camera_pan_sensitivity", self.context.camera_pan_sensitivity))),
        )
        self.context.camera_zoom_sensitivity = max(
            0.1,
            min(3.0, float(state.get("camera_zoom_sensitivity", self.context.camera_zoom_sensitivity))),
        )
        self.context.command_stack.set_max_undo_steps(
            int(state.get("undo_depth", self.context.command_stack.max_undo_steps))
        )

        self.context.mirror_x_enabled = bool(state.get("mirror_x_enabled", self.context.mirror_x_enabled))
        self.context.mirror_y_enabled = bool(state.get("mirror_y_enabled", self.context.mirror_y_enabled))
        self.context.mirror_z_enabled = bool(state.get("mirror_z_enabled", self.context.mirror_z_enabled))
        self.context.mirror_x_offset = int(state.get("mirror_x_offset", self.context.mirror_x_offset))
        self.context.mirror_y_offset = int(state.get("mirror_y_offset", self.context.mirror_y_offset))
        self.context.mirror_z_offset = int(state.get("mirror_z_offset", self.context.mirror_z_offset))
        self.context.fill_max_cells = int(state.get("fill_max_cells", self.context.fill_max_cells))

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
        self._autosave_timer.stop()
        self._autosave_debounce_timer.stop()
        clear_recovery_snapshot()
        settings = get_settings()
        settings.setValue("main_window/geometry", self.saveGeometry())
        settings.setValue("main_window/state", self.saveState())
        super().closeEvent(event)

    def _on_autosave_tick(self) -> None:
        self._save_recovery_snapshot_now()

    def _save_recovery_snapshot_now(self) -> None:
        try:
            self.context.current_project.editor_state = self._capture_editor_state()
            save_recovery_snapshot(self.context.current_project)
        except Exception:
            logging.getLogger("voxel_tool").exception("Autosave recovery snapshot failed")

    def _prompt_recovery_if_available(self) -> None:
        if not has_recovery_snapshot():
            return
        answer = QMessageBox.question(
            self,
            "Recovery Available",
            "An autosave recovery snapshot was found from a previous session.\n\nRestore it now?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer != QMessageBox.Yes:
            clear_recovery_snapshot()
            return
        try:
            project = load_recovery_snapshot()
        except Exception as exc:
            diagnostic_path = ""
            try:
                diagnostic_path = str(write_recovery_diagnostic(str(exc), stage="load"))
            except Exception:
                logging.getLogger("voxel_tool").exception("Failed to write recovery diagnostics")
            detail = f"Failed to load recovery snapshot.\n\n{exc}"
            if diagnostic_path:
                detail += f"\n\nDiagnostics: {diagnostic_path}"
            QMessageBox.warning(self, "Recovery Failed", detail)
            clear_recovery_snapshot()
            return
        self.context.current_project = project
        self.context.current_path = None
        self._apply_editor_state(project.editor_state)
        self.context.command_stack.clear()
        self.viewport.frame_to_voxels()
        self._show_voxel_status("Recovered autosave snapshot")

