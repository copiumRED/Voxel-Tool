from __future__ import annotations

import struct

from core.voxels.voxel_grid import VoxelGrid


def load_qb_models(path: str) -> tuple[list[VoxelGrid], list[tuple[int, int, int]]]:
    models, palette, _warnings = load_qb_models_with_warnings(path)
    return models, palette


def load_qb_models_with_warnings(path: str) -> tuple[list[VoxelGrid], list[tuple[int, int, int]], list[str]]:
    payload = open(path, "rb").read()
    if len(payload) < 24:
        raise ValueError("Invalid QB payload.")
    offset = 0
    version, color_format, _z_axis, compressed, _visibility, matrix_count = struct.unpack(
        "<IIIIII", payload[offset : offset + 24]
    )
    offset += 24
    if version == 0:
        raise ValueError("Unsupported QB version.")

    warnings: list[str] = []
    if compressed:
        raise ValueError("Compressed QB is not supported in this feasibility slice.")

    models: list[VoxelGrid] = []
    palette: list[tuple[int, int, int]] = []
    color_to_index: dict[tuple[int, int, int], int] = {}

    for _ in range(matrix_count):
        if offset >= len(payload):
            break
        name_len = payload[offset]
        offset += 1
        if offset + name_len > len(payload):
            raise ValueError("Invalid QB matrix name length.")
        offset += name_len  # name bytes unused in this slice
        if offset + 24 > len(payload):
            raise ValueError("Invalid QB matrix header size.")
        size_x, size_y, size_z, pos_x, pos_y, pos_z = struct.unpack("<IIIiii", payload[offset : offset + 24])
        offset += 24
        voxel_words = size_x * size_y * size_z
        byte_count = voxel_words * 4
        if offset + byte_count > len(payload):
            raise ValueError("Invalid QB voxel payload size.")
        voxels = VoxelGrid()
        for z in range(size_z):
            for y in range(size_y):
                for x in range(size_x):
                    raw = struct.unpack("<I", payload[offset : offset + 4])[0]
                    offset += 4
                    a = (raw >> 24) & 0xFF
                    b = (raw >> 16) & 0xFF
                    g = (raw >> 8) & 0xFF
                    r = raw & 0xFF
                    if a == 0:
                        continue
                    rgb = (r, g, b) if color_format == 0 else (b, g, r)
                    color_index = color_to_index.get(rgb)
                    if color_index is None:
                        color_index = len(palette)
                        palette.append(rgb)
                        color_to_index[rgb] = color_index
                    voxels.set(int(x) + int(pos_x), int(y) + int(pos_y), int(z) + int(pos_z), color_index)
        models.append(voxels)

    if not models:
        raise ValueError("QB file missing model data.")
    if not palette:
        palette = [(0, 0, 0)]
    return models, palette, warnings

