from __future__ import annotations

import json
import uuid

import pytest

from core.io.palette_io import load_palette_preset, save_palette_preset
from core.palette import add_palette_color, clamp_active_color_index, remove_palette_color, swap_palette_colors
from util.fs import get_app_temp_dir


def test_palette_preset_roundtrip() -> None:
    palette = [(1, 2, 3), (10, 20, 30), (220, 210, 200)]
    path = get_app_temp_dir("VoxelTool") / f"palette-{uuid.uuid4().hex}.json"
    try:
        save_palette_preset(palette, str(path))
        loaded = load_palette_preset(str(path))
        assert loaded == palette
    finally:
        path.unlink(missing_ok=True)


def test_palette_preset_load_validation() -> None:
    path = get_app_temp_dir("VoxelTool") / f"palette-invalid-{uuid.uuid4().hex}.json"
    try:
        path.write_text(json.dumps({"palette": [[0, 0], [1, 2, 3]]}), encoding="utf-8")
        with pytest.raises(ValueError):
            load_palette_preset(str(path))
    finally:
        path.unlink(missing_ok=True)


def test_clamp_active_color_index_keeps_index_valid() -> None:
    assert clamp_active_color_index(5, 3) == 2
    assert clamp_active_color_index(-1, 3) == 0
    assert clamp_active_color_index(1, 3) == 1


def test_palette_add_remove_swap_helpers() -> None:
    palette = [(10, 20, 30), (40, 50, 60)]
    next_palette = add_palette_color(palette, (1, 2, 3), index=1)
    assert next_palette == [(10, 20, 30), (1, 2, 3), (40, 50, 60)]

    swapped = swap_palette_colors(next_palette, 0, 2)
    assert swapped == [(40, 50, 60), (1, 2, 3), (10, 20, 30)]

    removed = remove_palette_color(swapped, 1)
    assert removed == [(40, 50, 60), (10, 20, 30)]
