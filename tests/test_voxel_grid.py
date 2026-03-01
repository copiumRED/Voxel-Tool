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


def test_voxel_grid_revision_increments_only_on_mutation() -> None:
    grid = VoxelGrid()
    assert grid.revision == 0
    grid.set(1, 2, 3, 4)
    assert grid.revision == 1
    grid.set(1, 2, 3, 4)
    assert grid.revision == 1
    grid.set(1, 2, 3, 5)
    assert grid.revision == 2
    grid.remove(9, 9, 9)
    assert grid.revision == 2
    grid.remove(1, 2, 3)
    assert grid.revision == 3
    grid.clear()
    assert grid.revision == 3
    grid.set(0, 0, 0, 1)
    grid.clear()
    assert grid.revision == 5
