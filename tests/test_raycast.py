from __future__ import annotations

from core.voxels.raycast import raycast_voxel_surface
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
