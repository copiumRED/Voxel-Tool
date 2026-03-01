from __future__ import annotations

import struct
from dataclasses import dataclass

from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class QbExportStats:
    voxel_count: int
    size: tuple[int, int, int]


def export_voxels_to_qb(
    voxels: VoxelGrid,
    palette: list[tuple[int, int, int]],
    path: str,
    *,
    matrix_name: str = "VoxelTool",
) -> QbExportStats:
    rows = voxels.to_list()
    if not rows:
        payload = _build_qb_payload([], matrix_name=matrix_name)
        with open(path, "wb") as file_obj:
            file_obj.write(payload)
        return QbExportStats(voxel_count=0, size=(0, 0, 0))

    xs = [x for x, _y, _z, _c in rows]
    ys = [y for _x, y, _z, _c in rows]
    zs = [z for _x, _y, z, _c in rows]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    size_x = max_x - min_x + 1
    size_y = max_y - min_y + 1
    size_z = max_z - min_z + 1
    voxel_map: dict[tuple[int, int, int], int] = {}
    for x, y, z, color in rows:
        voxel_map[(x - min_x, y - min_y, z - min_z)] = int(color)

    payload = _build_qb_payload(
        [
            {
                "name": matrix_name,
                "size": (size_x, size_y, size_z),
                "pos": (min_x, min_y, min_z),
                "voxels": voxel_map,
            }
        ],
        palette=palette,
        matrix_name=matrix_name,
    )
    with open(path, "wb") as file_obj:
        file_obj.write(payload)
    return QbExportStats(voxel_count=len(rows), size=(size_x, size_y, size_z))


def _build_qb_payload(
    matrices: list[dict[str, object]],
    *,
    palette: list[tuple[int, int, int]] | None = None,
    matrix_name: str = "VoxelTool",
) -> bytes:
    header = struct.pack("<IIIIII", 257, 0, 0, 0, 0, len(matrices))
    body = b""
    for matrix in matrices:
        name_text = str(matrix.get("name", matrix_name))
        name = name_text.encode("utf-8")
        if len(name) > 255:
            name = name[:255]
        sx, sy, sz = matrix["size"]
        px, py, pz = matrix["pos"]
        voxel_map: dict[tuple[int, int, int], int] = matrix["voxels"]  # type: ignore[assignment]
        body += struct.pack("<B", len(name)) + name
        body += struct.pack("<IIIiii", int(sx), int(sy), int(sz), int(px), int(py), int(pz))
        for z in range(int(sz)):
            for y in range(int(sy)):
                for x in range(int(sx)):
                    color_index = voxel_map.get((x, y, z))
                    if color_index is None:
                        body += struct.pack("<I", 0)
                        continue
                    rgb = (0, 0, 0)
                    if palette and 0 <= int(color_index) < len(palette):
                        rgb = palette[int(color_index)]
                    r, g, b = rgb
                    value = (int(r) & 0xFF) | ((int(g) & 0xFF) << 8) | ((int(b) & 0xFF) << 16) | (255 << 24)
                    body += struct.pack("<I", value)
    return header + body

