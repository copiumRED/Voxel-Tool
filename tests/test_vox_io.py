from __future__ import annotations

import struct
import uuid

from core.export.vox_exporter import export_voxels_to_vox
from core.io.vox_io import load_vox, load_vox_models
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


def test_load_vox_models_parses_multiple_models() -> None:
    path = get_app_temp_dir("VoxelTool") / f"vox-import-multi-{uuid.uuid4().hex}.vox"
    try:
        payload = _build_multi_model_vox_payload()
        path.write_bytes(payload)
        models, palette = load_vox_models(str(path))
        assert len(models) == 2
        assert models[0].count() == 1
        assert models[0].get(0, 0, 0) == 1
        assert models[1].count() == 1
        assert models[1].get(1, 0, 0) == 2
        assert palette[0] == (10, 20, 30)
        assert palette[1] == (40, 50, 60)
    finally:
        path.unlink(missing_ok=True)


def _chunk(chunk_id: bytes, content: bytes, children: bytes = b"") -> bytes:
    return chunk_id + struct.pack("<II", len(content), len(children)) + content + children


def _build_multi_model_vox_payload() -> bytes:
    size_a = _chunk(b"SIZE", struct.pack("<III", 2, 1, 1))
    xyzi_a = _chunk(b"XYZI", struct.pack("<I", 1) + struct.pack("<BBBB", 0, 0, 0, 2))
    size_b = _chunk(b"SIZE", struct.pack("<III", 2, 1, 1))
    xyzi_b = _chunk(b"XYZI", struct.pack("<I", 1) + struct.pack("<BBBB", 1, 0, 0, 3))
    rgba = b""
    for i in range(256):
        if i == 0:
            rgba += struct.pack("<BBBB", 10, 20, 30, 255)
        elif i == 1:
            rgba += struct.pack("<BBBB", 40, 50, 60, 255)
        elif i == 255:
            rgba += struct.pack("<BBBB", 0, 0, 0, 0)
        else:
            rgba += struct.pack("<BBBB", 0, 0, 0, 255)
    rgba_chunk = _chunk(b"RGBA", rgba)
    children = size_a + xyzi_a + size_b + xyzi_b + rgba_chunk
    main = _chunk(b"MAIN", b"", children)
    return b"VOX " + struct.pack("<I", 150) + main

