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


def test_export_vox_palette_index_mapping_is_stable() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(1, 0, 0, 1)
    voxels.set(2, 0, 0, 254)
    voxels.set(3, 0, 0, 255)
    voxels.set(4, 0, 0, 510)
    path = get_app_temp_dir("VoxelTool") / f"vox-export-palette-map-{uuid.uuid4().hex}.vox"
    try:
        export_voxels_to_vox(voxels, list(DEFAULT_PALETTE), str(path))
        data = path.read_bytes()
        entries = _read_xyzi_entries(data)
        colors = [entry[3] for entry in entries]
        assert colors == [1, 2, 255, 1, 1]
    finally:
        path.unlink(missing_ok=True)


def test_export_vox_rgba_chunk_uses_palette_prefix_and_alpha() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    custom_palette = [(10, 20, 30), (40, 50, 60), (70, 80, 90)]
    path = get_app_temp_dir("VoxelTool") / f"vox-export-rgba-{uuid.uuid4().hex}.vox"
    try:
        export_voxels_to_vox(voxels, custom_palette, str(path))
        rgba = _read_rgba_entries(path.read_bytes())
        assert rgba[0] == (10, 20, 30, 255)
        assert rgba[1] == (40, 50, 60, 255)
        assert rgba[2] == (70, 80, 90, 255)
        assert rgba[254] == (0, 0, 0, 255)
        assert rgba[255] == (0, 0, 0, 0)
    finally:
        path.unlink(missing_ok=True)


def _read_xyzi_entries(payload: bytes) -> list[tuple[int, int, int, int]]:
    xyzi_index = payload.index(b"XYZI")
    content_size = struct.unpack("<I", payload[xyzi_index + 4 : xyzi_index + 8])[0]
    start = xyzi_index + 12
    voxel_count = struct.unpack("<I", payload[start : start + 4])[0]
    data = payload[start + 4 : start + content_size]
    entries: list[tuple[int, int, int, int]] = []
    for i in range(voxel_count):
        offset = i * 4
        entries.append(struct.unpack("<BBBB", data[offset : offset + 4]))
    return entries


def _read_rgba_entries(payload: bytes) -> list[tuple[int, int, int, int]]:
    rgba_index = payload.index(b"RGBA")
    content_size = struct.unpack("<I", payload[rgba_index + 4 : rgba_index + 8])[0]
    start = rgba_index + 12
    data = payload[start : start + content_size]
    entries: list[tuple[int, int, int, int]] = []
    for i in range(256):
        offset = i * 4
        entries.append(struct.unpack("<BBBB", data[offset : offset + 4]))
    return entries
