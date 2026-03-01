from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.voxels.voxel_grid import VoxelGrid

if TYPE_CHECKING:
    from core.meshing.mesh import SurfaceMesh


@dataclass(slots=True)
class Part:
    part_id: str
    name: str
    voxels: VoxelGrid = field(default_factory=VoxelGrid)
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    visible: bool = True
    locked: bool = False
    mesh_cache: "SurfaceMesh | None" = None
    dirty_bounds: tuple[int, int, int, int, int, int] | None = None

    def mark_dirty_cells(self, cells: set[tuple[int, int, int]]) -> None:
        if not cells:
            return
        xs = [cell[0] for cell in cells]
        ys = [cell[1] for cell in cells]
        zs = [cell[2] for cell in cells]
        next_bounds = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
        if self.dirty_bounds is None:
            self.dirty_bounds = next_bounds
            return
        min_x, max_x, min_y, max_y, min_z, max_z = self.dirty_bounds
        self.dirty_bounds = (
            min(min_x, next_bounds[0]),
            max(max_x, next_bounds[1]),
            min(min_y, next_bounds[2]),
            max(max_y, next_bounds[3]),
            min(min_z, next_bounds[4]),
            max(max_z, next_bounds[5]),
        )
