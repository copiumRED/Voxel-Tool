from __future__ import annotations

from app.app_context import AppContext
from app.ui.main_window import _edit_plane_for_view_preset


def test_edit_plane_for_view_preset_top_bottom_is_xz() -> None:
    assert _edit_plane_for_view_preset("top") == AppContext.EDIT_PLANE_XZ
    assert _edit_plane_for_view_preset("bottom") == AppContext.EDIT_PLANE_XZ


def test_edit_plane_for_view_preset_left_right_is_yz() -> None:
    assert _edit_plane_for_view_preset("left") == AppContext.EDIT_PLANE_YZ
    assert _edit_plane_for_view_preset("right") == AppContext.EDIT_PLANE_YZ


def test_edit_plane_for_view_preset_front_back_is_xy() -> None:
    assert _edit_plane_for_view_preset("front") == AppContext.EDIT_PLANE_XY
    assert _edit_plane_for_view_preset("back") == AppContext.EDIT_PLANE_XY
