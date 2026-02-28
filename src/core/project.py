from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.voxels.voxel_grid import VoxelGrid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Project:
    name: str
    created_utc: str = field(default_factory=utc_now_iso)
    modified_utc: str = field(default_factory=utc_now_iso)
    version: int = 1
    voxels: VoxelGrid = field(default_factory=VoxelGrid)
