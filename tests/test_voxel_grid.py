from __future__ import annotations

from core.voxels.voxel_grid import VoxelGrid


def test_voxel_grid_roundtrip_list_conversion() -> None:
    grid = VoxelGrid()
    grid.set(1, 2, 3, 4)
    grid.set(-1, 0, 7, 2)
    grid.set(3, -2, 1, 6)

    rows = grid.to_list()
    restored = VoxelGrid.from_list(rows)

    assert restored.count() == grid.count()
    assert restored.to_list() == rows
