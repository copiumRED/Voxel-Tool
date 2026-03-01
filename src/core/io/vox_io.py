from __future__ import annotations

import struct

from core.voxels.voxel_grid import VoxelGrid


def load_vox(path: str) -> tuple[VoxelGrid, list[tuple[int, int, int]]]:
    models, palette = load_vox_models(path)
    if not models:
        return VoxelGrid(), palette
    return models[0], palette


def load_vox_models(path: str) -> tuple[list[VoxelGrid], list[tuple[int, int, int]]]:
    models, palette, _warnings = load_vox_models_with_warnings(path)
    return models, palette


def load_vox_models_with_warnings(path: str) -> tuple[list[VoxelGrid], list[tuple[int, int, int]], list[str]]:
    payload = open(path, "rb").read()
    if payload[:4] != b"VOX ":
        raise ValueError("Invalid VOX header.")
    if len(payload) < 20:
        raise ValueError("Invalid VOX payload.")

    models: list[VoxelGrid] = []
    palette: list[tuple[int, int, int]] = []
    unsupported_chunks: set[str] = set()
    pending_size: tuple[int, int, int] | None = None

    offset = 8
    while offset + 12 <= len(payload):
        chunk_id = payload[offset : offset + 4]
        content_size = struct.unpack("<I", payload[offset + 4 : offset + 8])[0]
        _children_size = struct.unpack("<I", payload[offset + 8 : offset + 12])[0]
        content_start = offset + 12
        content_end = content_start + content_size
        if content_end > len(payload):
            break
        content = payload[content_start:content_end]

        if chunk_id == b"SIZE" and len(content) >= 12:
            sx, sy, sz = struct.unpack("<III", content[:12])
            pending_size = (sx, sy, sz)
        elif chunk_id == b"XYZI" and len(content) >= 4:
            voxel_count = struct.unpack("<I", content[:4])[0]
            expected = 4 + (voxel_count * 4)
            if len(content) < expected:
                raise ValueError("Invalid VOX XYZI chunk size.")
            if pending_size is None:
                raise ValueError("VOX file has XYZI chunk without preceding SIZE chunk.")
            model = VoxelGrid()
            for i in range(voxel_count):
                start = 4 + (i * 4)
                x, y, z, color = struct.unpack("<BBBB", content[start : start + 4])
                if color == 0:
                    continue
                model.set(int(x), int(y), int(z), int(color - 1))
            models.append(model)
            pending_size = None
        elif chunk_id == b"RGBA" and len(content) >= 1024:
            palette = []
            for i in range(255):
                rgba = struct.unpack("<BBBB", content[i * 4 : (i * 4) + 4])
                palette.append((int(rgba[0]), int(rgba[1]), int(rgba[2])))
        elif chunk_id not in {b"MAIN"}:
            unsupported_chunks.add(chunk_id.decode("ascii", errors="replace"))

        offset = content_end

    if not models:
        raise ValueError("VOX file missing model data (SIZE/XYZI).")
    if not palette:
        palette = [(0, 0, 0)] * 255
    return models, palette, sorted(unsupported_chunks)

