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
    visible: bool = True
    locked: bool = False
    mesh_cache: "SurfaceMesh | None" = None
