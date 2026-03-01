from __future__ import annotations

from app.app_context import AppContext
from app.viewport.gl_widget import GLViewportWidget
from app.ui.main_window import _next_brush_size, _project_io_error_detail
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
