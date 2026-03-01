from __future__ import annotations

from app.ui.main_window import _next_brush_size


def test_next_brush_size_cycles_three_step_range() -> None:
    assert _next_brush_size(1) == 2
    assert _next_brush_size(2) == 3
    assert _next_brush_size(3) == 1


def test_next_brush_size_clamps_invalid_to_min() -> None:
    assert _next_brush_size(0) == 1
    assert _next_brush_size(99) == 1
