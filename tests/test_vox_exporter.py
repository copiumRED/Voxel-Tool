from __future__ import annotations

import struct
import uuid

from core.export.vox_exporter import export_voxels_to_vox
from core.palette import DEFAULT_PALETTE
from core.voxels.voxel_grid import VoxelGrid
from util.fs import get_app_temp_dir


def test_export_vox_writes_header_and_main_chunks() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(1, 0, 0, 1)
    path = get_app_temp_dir("VoxelTool") / f"vox-export-{uuid.uuid4().hex}.vox"
    try:
        stats = export_voxels_to_vox(voxels, list(DEFAULT_PALETTE), str(path))
        data = path.read_bytes()
        assert data[:4] == b"VOX "
        assert struct.unpack("<I", data[4:8])[0] == 150
        assert b"MAIN" in data
        assert b"SIZE" in data
        assert b"XYZI" in data
        assert b"RGBA" in data
        assert stats.voxel_count == 2
    finally:
        path.unlink(missing_ok=True)


def test_export_vox_normalizes_negative_coordinates() -> None:
    voxels = VoxelGrid()
    voxels.set(-2, -1, 0, 2)
    voxels.set(0, 1, 2, 3)
    path = get_app_temp_dir("VoxelTool") / f"vox-export-neg-{uuid.uuid4().hex}.vox"
    try:
        stats = export_voxels_to_vox(voxels, list(DEFAULT_PALETTE), str(path))
        assert stats.size == (3, 3, 3)
        data = path.read_bytes()
        xyzi_index = data.index(b"XYZI")
        content_size = struct.unpack("<I", data[xyzi_index + 4 : xyzi_index + 8])[0]
        assert content_size == 4 + (2 * 4)
    finally:
        path.unlink(missing_ok=True)
