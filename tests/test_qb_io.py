from __future__ import annotations

import struct
import uuid

import pytest

from core.io.qb_io import load_qb_models, load_qb_models_with_warnings
from util.fs import get_app_temp_dir


def test_load_qb_models_parses_single_matrix_with_position_offset() -> None:
    path = get_app_temp_dir("VoxelTool") / f"qb-import-{uuid.uuid4().hex}.qb"
    try:
        path.write_bytes(
            _build_qb_payload(
                [
                    {
                        "name": "MatrixA",
                        "size": (2, 1, 1),
                        "pos": (3, 2, 1),
                        "voxels": [
                            (0, 0, 0, (255, 0, 0, 255)),
                            (1, 0, 0, (0, 255, 0, 255)),
                        ],
                    }
                ]
            )
        )
        models, palette = load_qb_models(str(path))
        assert len(models) == 1
        assert models[0].get(3, 2, 1) == 0
        assert models[0].get(4, 2, 1) == 1
        assert palette[0] == (255, 0, 0)
        assert palette[1] == (0, 255, 0)
    finally:
        path.unlink(missing_ok=True)


def test_load_qb_models_with_warnings_rejects_compressed_payload() -> None:
    path = get_app_temp_dir("VoxelTool") / f"qb-import-compressed-{uuid.uuid4().hex}.qb"
    try:
        path.write_bytes(_build_qb_payload([], compressed=1))
        with pytest.raises(ValueError, match="Compressed QB"):
            load_qb_models_with_warnings(str(path))
    finally:
        path.unlink(missing_ok=True)


def _pack_color_rgba(r: int, g: int, b: int, a: int) -> bytes:
    value = (int(r) & 0xFF) | ((int(g) & 0xFF) << 8) | ((int(b) & 0xFF) << 16) | ((int(a) & 0xFF) << 24)
    return struct.pack("<I", value)


def _build_qb_payload(matrices: list[dict[str, object]], *, compressed: int = 0) -> bytes:
    header = struct.pack("<IIIIII", 257, 0, 0, int(compressed), 0, len(matrices))
    body = b""
    for matrix in matrices:
        name = str(matrix["name"]).encode("utf-8")
        sx, sy, sz = matrix["size"]
        px, py, pz = matrix["pos"]
        body += struct.pack("<B", len(name)) + name
        body += struct.pack("<IIIiii", int(sx), int(sy), int(sz), int(px), int(py), int(pz))
        voxel_map: dict[tuple[int, int, int], tuple[int, int, int, int]] = {}
        for x, y, z, rgba in matrix["voxels"]:
            voxel_map[(int(x), int(y), int(z))] = rgba
        for z in range(int(sz)):
            for y in range(int(sy)):
                for x in range(int(sx)):
                    rgba = voxel_map.get((x, y, z), (0, 0, 0, 0))
                    body += _pack_color_rgba(*rgba)
    return header + body

