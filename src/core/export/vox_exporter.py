from __future__ import annotations

import struct
from dataclasses import dataclass

from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class VoxExportStats:
    voxel_count: int
    size: tuple[int, int, int]


def export_voxels_to_vox(
    voxels: VoxelGrid,
    palette: list[tuple[int, int, int]],
    path: str,
) -> VoxExportStats:
    rows = voxels.to_list()
    if not rows:
        size = (1, 1, 1)
        payload = _build_vox_payload([], size, palette)
        with open(path, "wb") as file_obj:
            file_obj.write(payload)
        return VoxExportStats(voxel_count=0, size=size)

    xs = [row[0] for row in rows]
    ys = [row[1] for row in rows]
    zs = [row[2] for row in rows]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    size = (max_x - min_x + 1, max_y - min_y + 1, max_z - min_z + 1)
    if any(component > 255 for component in size):
        raise ValueError("VOX export supports maximum model size of 255 on each axis.")
    if len(rows) > 255 * 255 * 255:
        raise ValueError("VOX export voxel count exceeds single-model limits.")

    vox_entries: list[tuple[int, int, int, int]] = []
    for x, y, z, color_index in rows:
        vx = x - min_x
        vy = y - min_y
        vz = z - min_z
        vox_color = (color_index % 255) + 1
        vox_entries.append((vx, vy, vz, vox_color))

    payload = _build_vox_payload(vox_entries, size, palette)
    with open(path, "wb") as file_obj:
        file_obj.write(payload)
    return VoxExportStats(voxel_count=len(vox_entries), size=size)


def _build_vox_payload(
    entries: list[tuple[int, int, int, int]],
    size: tuple[int, int, int],
    palette: list[tuple[int, int, int]],
) -> bytes:
    size_chunk_content = struct.pack("<III", size[0], size[1], size[2])
    size_chunk = _chunk(b"SIZE", size_chunk_content, b"")

    xyzi_payload = struct.pack("<I", len(entries))
    for x, y, z, color in entries:
        xyzi_payload += struct.pack("<BBBB", x, y, z, color)
    xyzi_chunk = _chunk(b"XYZI", xyzi_payload, b"")

    rgba_bytes = b""
    for i in range(256):
        if i == 255:
            rgba_bytes += struct.pack("<BBBB", 0, 0, 0, 0)
            continue
        if i < len(palette):
            r, g, b = palette[i]
        else:
            r, g, b = 0, 0, 0
        rgba_bytes += struct.pack("<BBBB", int(r), int(g), int(b), 255)
    rgba_chunk = _chunk(b"RGBA", rgba_bytes, b"")

    children = size_chunk + xyzi_chunk + rgba_chunk
    main_chunk = _chunk(b"MAIN", b"", children)
    return b"VOX " + struct.pack("<I", 150) + main_chunk


def _chunk(chunk_id: bytes, content: bytes, children: bytes) -> bytes:
    return chunk_id + struct.pack("<II", len(content), len(children)) + content + children
