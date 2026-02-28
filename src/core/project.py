from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.scene import Scene
from core.voxels.voxel_grid import VoxelGrid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Project:
    name: str
    created_utc: str = field(default_factory=utc_now_iso)
    modified_utc: str = field(default_factory=utc_now_iso)
    version: int = 1
    scene: Scene = field(default_factory=Scene.with_default_part)
    editor_state: dict[str, object] = field(default_factory=dict)

    @property
    def active_part_id(self) -> str:
        return self.scene.get_active_part().part_id

    @property
    def voxels(self) -> VoxelGrid:
        return self.scene.get_active_part().voxels

    @voxels.setter
    def voxels(self, value: VoxelGrid) -> None:
        self.scene.get_active_part().voxels = value
