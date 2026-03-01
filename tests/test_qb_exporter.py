from __future__ import annotations

import uuid

from core.export.qb_exporter import export_voxels_to_qb
from core.io.qb_io import load_qb_models
from core.voxels.voxel_grid import VoxelGrid
from util.fs import get_app_temp_dir


def test_export_qb_roundtrip_with_importer() -> None:
    voxels = VoxelGrid()
    voxels.set(-1, 0, 2, 0)
    voxels.set(1, 2, 3, 1)
    palette = [(10, 20, 30), (40, 50, 60)]
    path = get_app_temp_dir("VoxelTool") / f"qb-export-{uuid.uuid4().hex}.qb"
    try:
        stats = export_voxels_to_qb(voxels, palette, str(path), matrix_name="RoundTrip")
        assert stats.voxel_count == 2
        assert path.exists()
        models, loaded_palette = load_qb_models(str(path))
        assert len(models) == 1
        assert models[0].get(-1, 0, 2) == 0
        assert models[0].get(1, 2, 3) == 1
        assert loaded_palette[0] == (10, 20, 30)
        assert loaded_palette[1] == (40, 50, 60)
    finally:
        path.unlink(missing_ok=True)


def test_export_qb_empty_voxel_grid() -> None:
    voxels = VoxelGrid()
    path = get_app_temp_dir("VoxelTool") / f"qb-export-empty-{uuid.uuid4().hex}.qb"
    try:
        stats = export_voxels_to_qb(voxels, [(0, 0, 0)], str(path))
        assert stats.voxel_count == 0
        assert stats.size == (0, 0, 0)
        assert path.exists()
    finally:
        path.unlink(missing_ok=True)

