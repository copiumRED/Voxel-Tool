from __future__ import annotations

from app.ui.panels.stats_panel import format_runtime_stats_label


def test_format_runtime_stats_label_includes_scene_and_active_scope() -> None:
    text = format_runtime_stats_label(
        frame_ms=16.66,
        rebuild_ms=4.2,
        scene_triangles=123,
        scene_voxels=77,
        active_part_voxels=12,
    )
    assert "scene tris 123" in text
    assert "scene voxels 77" in text
    assert "active-part voxels 12" in text
