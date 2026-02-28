from __future__ import annotations

from core.voxels.raycast import raycast_voxel_surface, resolve_brush_target_cell
from core.voxels.voxel_grid import VoxelGrid


def test_raycast_hits_first_voxel_and_returns_previous_cell() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    voxels.set(1, 0, 0, 2)

    result = raycast_voxel_surface(
        voxels,
        origin=(-5.0, 0.0, 0.0),
        direction=(1.0, 0.0, 0.0),
        max_distance=20.0,
        step_size=0.1,
    )
    assert result is not None
    hit_cell, previous_cell = result
    assert hit_cell == (0, 0, 0)
    assert previous_cell == (-1, 0, 0)


def test_raycast_returns_none_when_no_hit() -> None:
    voxels = VoxelGrid()
    result = raycast_voxel_surface(
        voxels,
        origin=(0.0, 10.0, 0.0),
        direction=(1.0, 0.0, 0.0),
        max_distance=10.0,
        step_size=0.2,
    )
    assert result is None


def test_resolve_brush_target_uses_surface_adjacent_for_paint() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)

    result = resolve_brush_target_cell(
        voxels,
        origin=(-5.0, 0.0, 0.0),
        direction=(1.0, 0.0, 0.0),
        erase_mode=False,
        plane_fallback_cell=(3, 3, 0),
    )
    assert result == ((-1, 0, 0), "surface-adjacent")


def test_resolve_brush_target_uses_plane_fallback_when_no_surface_hit() -> None:
    voxels = VoxelGrid()
    result = resolve_brush_target_cell(
        voxels,
        origin=(0.0, 3.0, 2.0),
        direction=(1.0, 0.0, 0.0),
        erase_mode=False,
        plane_fallback_cell=(4, 5, 0),
    )
    assert result == ((4, 5, 0), "plane-fallback")


def test_resolve_brush_target_in_erase_mode_requires_surface_hit() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 2)
    hit_result = resolve_brush_target_cell(
        voxels,
        origin=(-4.0, 0.0, 0.0),
        direction=(1.0, 0.0, 0.0),
        erase_mode=True,
        plane_fallback_cell=(9, 9, 0),
    )
    miss_result = resolve_brush_target_cell(
        voxels,
        origin=(0.0, 6.0, 0.0),
        direction=(1.0, 0.0, 0.0),
        erase_mode=True,
        plane_fallback_cell=(9, 9, 0),
    )
    assert hit_result == ((0, 0, 0), "surface")
    assert miss_result is None
