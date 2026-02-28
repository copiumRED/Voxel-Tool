from __future__ import annotations

import uuid

from core.export.vox_exporter import export_voxels_to_vox
from core.io.vox_io import load_vox
from core.palette import DEFAULT_PALETTE
from core.voxels.voxel_grid import VoxelGrid
from util.fs import get_app_temp_dir


def test_load_vox_roundtrip_from_exporter() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    voxels.set(2, 1, 0, 4)
    path = get_app_temp_dir("VoxelTool") / f"vox-import-{uuid.uuid4().hex}.vox"
    try:
        export_voxels_to_vox(voxels, list(DEFAULT_PALETTE), str(path))
        loaded_voxels, loaded_palette = load_vox(str(path))
        assert loaded_voxels.count() == 2
        assert loaded_voxels.get(0, 0, 0) == 1
        assert loaded_voxels.get(2, 1, 0) == 4
        assert loaded_palette[0] == DEFAULT_PALETTE[0]
        assert loaded_palette[1] == DEFAULT_PALETTE[1]
    finally:
        path.unlink(missing_ok=True)

