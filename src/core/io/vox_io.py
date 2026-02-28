from __future__ import annotations

import struct

from core.voxels.voxel_grid import VoxelGrid


def load_vox(path: str) -> tuple[VoxelGrid, list[tuple[int, int, int]]]:
    payload = open(path, "rb").read()
    if payload[:4] != b"VOX ":
        raise ValueError("Invalid VOX header.")
    if len(payload) < 20:
        raise ValueError("Invalid VOX payload.")

    size: tuple[int, int, int] | None = None
    voxels = VoxelGrid()
    palette: list[tuple[int, int, int]] = []

    offset = 8
    while offset + 12 <= len(payload):
        chunk_id = payload[offset : offset + 4]
        content_size = struct.unpack("<I", payload[offset + 4 : offset + 8])[0]
        children_size = struct.unpack("<I", payload[offset + 8 : offset + 12])[0]
        content_start = offset + 12
        content_end = content_start + content_size
        if content_end > len(payload):
            break
        content = payload[content_start:content_end]

        if chunk_id == b"SIZE" and len(content) >= 12 and size is None:
            sx, sy, sz = struct.unpack("<III", content[:12])
            size = (sx, sy, sz)
        elif chunk_id == b"XYZI" and len(content) >= 4:
            voxel_count = struct.unpack("<I", content[:4])[0]
            expected = 4 + (voxel_count * 4)
            if len(content) < expected:
                raise ValueError("Invalid VOX XYZI chunk size.")
            for i in range(voxel_count):
                start = 4 + (i * 4)
                x, y, z, color = struct.unpack("<BBBB", content[start : start + 4])
                if color == 0:
                    continue
                voxels.set(int(x), int(y), int(z), int(color - 1))
        elif chunk_id == b"RGBA" and len(content) >= 1024:
            palette = []
            for i in range(255):
                rgba = struct.unpack("<BBBB", content[i * 4 : (i * 4) + 4])
                palette.append((int(rgba[0]), int(rgba[1]), int(rgba[2])))

        offset = content_end

    if size is None:
        raise ValueError("VOX file missing SIZE chunk.")
    if not palette:
        palette = [(0, 0, 0)] * 255
    return voxels, palette
