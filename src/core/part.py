from __future__ import annotations

from dataclasses import dataclass, field

from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class Part:
    part_id: str
    name: str
    voxels: VoxelGrid = field(default_factory=VoxelGrid)
    visible: bool = True
    locked: bool = False
