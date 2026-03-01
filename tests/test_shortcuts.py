from __future__ import annotations

from app.app_context import AppContext
from app.viewport.gl_widget import GLViewportWidget
from app.ui.main_window import _next_brush_size
from core.project import Project


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
