from __future__ import annotations

from app.app_context import AppContext
from app.viewport.gl_widget import GLViewportWidget
from app.ui.main_window import (
    _app_theme_stylesheet,
    _duplicate_shortcut_sequences,
    _format_hotkey_overlay_text,
    _next_brush_size,
    _filter_command_palette_entries,
    _layout_preset_state_key,
    _project_io_error_detail,
    _quick_toolbar_action_labels,
    _vox_import_group_name,
    _vox_import_part_name,
)
from app.ui.panels.palette_panel import PalettePanel
from core.project import Project
from PySide6.QtCore import Qt
from pathlib import Path
import pytest


def test_next_brush_size_cycles_three_step_range() -> None:
    assert _next_brush_size(1) == 2
    assert _next_brush_size(2) == 3
    assert _next_brush_size(3) == 1


def test_next_brush_size_clamps_invalid_to_min() -> None:
    assert _next_brush_size(0) == 1
    assert _next_brush_size(99) == 1


def test_left_interaction_mode_prefers_edit_for_voxel_tools() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    for shape in (
        ctx.TOOL_SHAPE_BRUSH,
        ctx.TOOL_SHAPE_BOX,
        ctx.TOOL_SHAPE_LINE,
        ctx.TOOL_SHAPE_FILL,
    ):
        ctx.set_voxel_tool_shape(shape)
        assert GLViewportWidget._resolve_left_interaction_mode(ctx) == GLViewportWidget._LEFT_INTERACTION_EDIT


def test_left_interaction_mode_defaults_to_navigate_without_context() -> None:
    assert (
        GLViewportWidget._resolve_left_interaction_mode(None) == GLViewportWidget._LEFT_INTERACTION_NAVIGATE
    )


def test_mmb_orbit_profile_switches_left_navigate_orbit_behavior() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    assert GLViewportWidget._left_navigate_orbits(ctx) is True
    ctx.set_navigation_profile(AppContext.NAV_PROFILE_MMB_ORBIT)
    assert GLViewportWidget._is_mmb_orbit_enabled(ctx) is True
    assert GLViewportWidget._left_navigate_orbits(ctx) is False


def test_blender_mix_profile_enables_shift_middle_pan_modifier() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    ctx.set_navigation_profile(AppContext.NAV_PROFILE_BLENDER_MIX)
    assert GLViewportWidget._is_mmb_orbit_enabled(ctx) is True
    assert GLViewportWidget._is_middle_drag_pan(ctx, Qt.ShiftModifier) is True


def test_camera_sensitivity_helpers_follow_context_values() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    ctx.set_camera_sensitivity("orbit", 1.5)
    ctx.set_camera_sensitivity("pan", 2.0)
    ctx.set_camera_sensitivity("zoom", 0.5)
    assert GLViewportWidget._orbit_sensitivity(ctx) == pytest.approx(0.6)
    assert GLViewportWidget._pan_sensitivity(ctx) == 2.0
    assert GLViewportWidget._zoom_sensitivity(ctx) == 0.5


def test_precision_scale_factor_reduces_camera_motion_when_alt_is_held() -> None:
    assert GLViewportWidget._precision_scale_factor(Qt.NoModifier) == pytest.approx(1.0)
    assert GLViewportWidget._precision_scale_factor(Qt.AltModifier) == pytest.approx(0.2)


def test_project_io_error_detail_includes_action_path_and_message() -> None:
    detail = _project_io_error_detail("Save Project", "C:/tmp/demo.json", RuntimeError("disk full"))
    assert "Save Project failed." in detail
    assert "C:/tmp/demo.json" in detail
    assert "disk full" in detail


def test_selection_mode_flag_enables_selection_interaction_mode() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    ctx.set_voxel_selection_mode(True)
    assert GLViewportWidget._is_selection_mode_enabled(ctx) is True
    assert GLViewportWidget._resolve_left_interaction_mode(ctx) == GLViewportWidget._LEFT_INTERACTION_EDIT


def test_selection_move_delta_map_covers_arrow_and_page_keys() -> None:
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_Left) == (-1, 0, 0)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_Right) == (1, 0, 0)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_Up) == (0, 1, 0)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_Down) == (0, -1, 0)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_PageUp) == (0, 0, 1)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_PageDown) == (0, 0, -1)
    assert GLViewportWidget._selection_move_delta_from_key(Qt.Key_A) is None


def test_mirror_guide_segments_respect_enabled_axes_and_offsets() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    assert GLViewportWidget._mirror_guide_segments(ctx) == []
    ctx.set_mirror_axis("x", True)
    ctx.set_mirror_offset("x", 3)

    segments = GLViewportWidget._mirror_guide_segments(ctx, extent=10.0, step=5)
    assert len(segments) > 0
    for start, end, _ in segments:
        assert start[0] == pytest.approx(3.0)
        assert end[0] == pytest.approx(3.0)


def test_mirror_overlay_label_lists_enabled_axes() -> None:
    ctx = AppContext(current_project=Project(name="Shortcut Input"))
    assert GLViewportWidget._mirror_overlay_label(ctx) == ""
    ctx.set_mirror_axis("x", True)
    ctx.set_mirror_axis("z", True)
    ctx.set_mirror_offset("x", -2)
    ctx.set_mirror_offset("z", 4)
    label = GLViewportWidget._mirror_overlay_label(ctx)
    assert "X@-2" in label
    assert "Z@4" in label


def test_palette_preset_filter_matches_case_insensitive_substrings() -> None:
    paths = [
        Path("WarmBase.json"),
        Path("cool-shades.gpl"),
        Path("terrain.json"),
    ]
    filtered = PalettePanel._filter_preset_paths(paths, "coo")
    assert [p.name for p in filtered] == ["cool-shades.gpl"]
    filtered_all = PalettePanel._filter_preset_paths(paths, "")
    assert [p.name for p in filtered_all] == ["cool-shades.gpl", "terrain.json", "WarmBase.json"]


def test_vox_import_naming_helpers_for_single_and_multi_part_imports() -> None:
    assert _vox_import_group_name("Robot") == "Robot Import"
    assert _vox_import_part_name("Robot", 0, 1) == "Robot"
    assert _vox_import_part_name("Robot", 0, 12) == "Robot Part 01"
    assert _vox_import_part_name("Robot", 11, 12) == "Robot Part 12"


def test_visible_render_signature_changes_when_voxel_revision_changes() -> None:
    ctx = AppContext(current_project=Project(name="Signature"))
    before = GLViewportWidget._compute_visible_render_signature(ctx)
    ctx.current_project.voxels.set(0, 0, 0, 1)
    after = GLViewportWidget._compute_visible_render_signature(ctx)
    assert before != after


def test_quick_toolbar_action_labels_include_expected_core_actions() -> None:
    labels = _quick_toolbar_action_labels()
    assert labels[:3] == ("New", "Open", "Save")
    assert "Undo" in labels and "Redo" in labels
    assert "Solidify" in labels
    assert "Export OBJ" in labels and "Export glTF" in labels and "Export VOX" in labels


def test_hud_badges_reflect_core_editing_state() -> None:
    ctx = AppContext(current_project=Project(name="HUD"))
    ctx.set_voxel_tool_shape(AppContext.TOOL_SHAPE_LINE)
    ctx.set_voxel_tool_mode(AppContext.TOOL_MODE_ERASE)
    ctx.set_pick_mode(AppContext.PICK_MODE_SURFACE)
    ctx.set_edit_plane(AppContext.EDIT_PLANE_YZ)
    ctx.set_camera_projection(AppContext.CAMERA_PROJECTION_ORTHOGRAPHIC)
    ctx.set_navigation_profile(AppContext.NAV_PROFILE_BLENDER_MIX)
    ctx.set_mirror_axis("x", True)
    badges = GLViewportWidget._hud_badges(ctx)
    assert "Tool:line/erase" in badges
    assert "Pick:surface" in badges
    assert "Plane:YZ" in badges
    assert "Mirror:X" in badges
    assert "Proj:orthographic" in badges
    assert "Nav:blender_mix" in badges


def test_command_palette_filter_returns_sorted_matches() -> None:
    entries = [
        ("export_obj", "Export OBJ"),
        ("open_project", "Open Project"),
        ("export_gltf", "Export glTF"),
    ]
    filtered = _filter_command_palette_entries(entries, "export")
    assert [label for _id, label in filtered] == ["Export glTF", "Export OBJ"]


def test_layout_preset_state_key_validation() -> None:
    assert _layout_preset_state_key(1) == "main_window/layout_preset_1"
    assert _layout_preset_state_key(2) == "main_window/layout_preset_2"
    with pytest.raises(ValueError):
        _layout_preset_state_key(3)


def test_duplicate_shortcut_sequence_detector_reports_conflicts() -> None:
    bindings = [("B", "Brush"), ("Shift+F", "Frame"), ("b", "Brush Alt")]
    conflicts = _duplicate_shortcut_sequences(bindings)
    assert conflicts == ("B",)


def test_duplicate_shortcut_sequence_detector_is_empty_when_unique() -> None:
    bindings = [("B", "Brush"), ("Shift+F", "Frame"), ("Ctrl+Shift+P", "Command Palette")]
    assert _duplicate_shortcut_sequences(bindings) == ()


def test_hotkey_overlay_text_contains_binding_labels() -> None:
    text = _format_hotkey_overlay_text([("B", "Tool: Brush"), ("Shift+F", "Frame Voxels")])
    assert "B" in text
    assert "Tool: Brush" in text
    assert "Shift+F" in text
    assert "Frame Voxels" in text


def test_app_theme_stylesheet_contains_key_widget_rules() -> None:
    css = _app_theme_stylesheet()
    assert "QMainWindow" in css
    assert "QToolBar" in css
    assert "QPushButton" in css
    assert "QStatusBar" in css
