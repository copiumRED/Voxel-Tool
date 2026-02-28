from __future__ import annotations

from app.app_context import AppContext
from core.palette import DEFAULT_PALETTE
from core.project import Project


def test_palette_defaults_and_active_index() -> None:
    assert len(DEFAULT_PALETTE) == 8

    ctx = AppContext(current_project=Project(name="Untitled"))
    assert len(ctx.palette) == 8
    assert ctx.active_color_index == 0
