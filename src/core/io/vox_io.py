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
    pending_translation = (0, 0, 0)

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
            tx, ty, tz = pending_translation
            for i in range(voxel_count):
                start = 4 + (i * 4)
                x, y, z, color = struct.unpack("<BBBB", content[start : start + 4])
                if color == 0:
                    continue
                model.set(int(x) + tx, int(y) + ty, int(z) + tz, int(color - 1))
            models.append(model)
            pending_size = None
            pending_translation = (0, 0, 0)
        elif chunk_id == b"nTRN":
            parsed_translation = _parse_ntrn_translation(content)
            if parsed_translation is None:
                unsupported_chunks.add("nTRN")
            else:
                pending_translation = parsed_translation
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


def _read_vox_dict(content: bytes, offset: int) -> tuple[dict[str, str], int] | None:
    if offset + 4 > len(content):
        return None
    count = struct.unpack("<i", content[offset : offset + 4])[0]
    offset += 4
    if count < 0:
        return None
    result: dict[str, str] = {}
    for _ in range(count):
        if offset + 4 > len(content):
            return None
        key_len = struct.unpack("<i", content[offset : offset + 4])[0]
        offset += 4
        if key_len < 0 or offset + key_len > len(content):
            return None
        key = content[offset : offset + key_len].decode("utf-8", errors="replace")
        offset += key_len
        if offset + 4 > len(content):
            return None
        value_len = struct.unpack("<i", content[offset : offset + 4])[0]
        offset += 4
        if value_len < 0 or offset + value_len > len(content):
            return None
        value = content[offset : offset + value_len].decode("utf-8", errors="replace")
        offset += value_len
        result[key] = value
    return result, offset


def _parse_ntrn_translation(content: bytes) -> tuple[int, int, int] | None:
    # nTRN (VOX 150): node_id | node_dict | child_id | reserved | layer_id | num_frames | frame_dict...
    if len(content) < 24:
        return None
    offset = 0
    offset += 4  # node_id
    node_dict_result = _read_vox_dict(content, offset)
    if node_dict_result is None:
        return None
    _node_dict, offset = node_dict_result
    if offset + 16 > len(content):
        return None
    offset += 12  # child_id, reserved_id, layer_id
    num_frames = struct.unpack("<i", content[offset : offset + 4])[0]
    offset += 4
    if num_frames <= 0:
        return (0, 0, 0)
    frame_dict_result = _read_vox_dict(content, offset)
    if frame_dict_result is None:
        return None
    frame_dict, _ = frame_dict_result
    raw_t = frame_dict.get("_t")
    if raw_t is None:
        return (0, 0, 0)
    parts = raw_t.strip().split()
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None

