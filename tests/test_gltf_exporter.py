from __future__ import annotations

import json
import base64
import struct
import uuid

from core.export.gltf_exporter import export_voxels_to_gltf
from core.voxels.voxel_grid import VoxelGrid
from util.fs import get_app_temp_dir


def test_export_gltf_smoke_non_empty_mesh_and_counts() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(1, 0, 0, 1)
    path = get_app_temp_dir("VoxelTool") / f"gltf-export-{uuid.uuid4().hex}.gltf"
    try:
        stats = export_voxels_to_gltf(voxels, str(path))
        assert path.exists()
        assert stats.vertex_count > 0
        assert stats.triangle_count > 0

        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["asset"]["version"] == "2.0"
        assert len(payload["meshes"]) == 1
        primitive = payload["meshes"][0]["primitives"][0]
        assert "NORMAL" in primitive["attributes"]
        assert primitive["attributes"]["NORMAL"] == 1
        assert primitive["attributes"]["TEXCOORD_0"] == 2
        assert primitive["attributes"]["COLOR_0"] == 3
        assert primitive["mode"] == 4
        assert payload["accessors"][1]["count"] == payload["accessors"][0]["count"]
        assert payload["accessors"][2]["type"] == "VEC2"
        assert payload["accessors"][2]["count"] == payload["accessors"][0]["count"]
        assert payload["accessors"][3]["type"] == "VEC3"
        assert payload["accessors"][4]["type"] == "SCALAR"
    finally:
        path.unlink(missing_ok=True)


def test_export_gltf_empty_mesh() -> None:
    voxels = VoxelGrid()
    path = get_app_temp_dir("VoxelTool") / f"gltf-export-empty-{uuid.uuid4().hex}.gltf"
    try:
        stats = export_voxels_to_gltf(voxels, str(path))
        assert path.exists()
        assert stats.vertex_count == 0
        assert stats.triangle_count == 0
    finally:
        path.unlink(missing_ok=True)


def test_export_gltf_applies_scale_factor_to_bounds() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    base_path = get_app_temp_dir("VoxelTool") / f"gltf-export-scale-base-{uuid.uuid4().hex}.gltf"
    scaled_path = get_app_temp_dir("VoxelTool") / f"gltf-export-scale-100-{uuid.uuid4().hex}.gltf"
    try:
        export_voxels_to_gltf(voxels, str(base_path), scale_factor=1.0)
        export_voxels_to_gltf(voxels, str(scaled_path), scale_factor=100.0)
        base_payload = json.loads(base_path.read_text(encoding="utf-8"))
        scaled_payload = json.loads(scaled_path.read_text(encoding="utf-8"))
        base_max = base_payload["accessors"][0]["max"][0]
        scaled_max = scaled_payload["accessors"][0]["max"][0]
        assert scaled_max == base_max * 100.0
    finally:
        base_path.unlink(missing_ok=True)
        scaled_path.unlink(missing_ok=True)


def test_export_gltf_vertex_colors_emit_multiple_values_for_multicolor_mesh() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    voxels.set(1, 0, 0, 2)
    path = get_app_temp_dir("VoxelTool") / f"gltf-export-vcolor-{uuid.uuid4().hex}.gltf"
    try:
        export_voxels_to_gltf(voxels, str(path))
        payload = json.loads(path.read_text(encoding="utf-8"))
        primitive = payload["meshes"][0]["primitives"][0]
        color_accessor_index = primitive["attributes"]["COLOR_0"]
        color_accessor = payload["accessors"][color_accessor_index]
        color_view = payload["bufferViews"][color_accessor["bufferView"]]
        encoded = payload["buffers"][0]["uri"].split(",", 1)[1]
        blob = base64.b64decode(encoded)
        raw = blob[color_view["byteOffset"] : color_view["byteOffset"] + color_view["byteLength"]]
        values = struct.unpack("<" + "f" * (len(raw) // 4), raw)
        rgb_values = [(values[i], values[i + 1], values[i + 2]) for i in range(0, len(values), 3)]
        distinct = {(round(r, 4), round(g, 4), round(b, 4)) for r, g, b in rgb_values}
        assert len(distinct) >= 2
    finally:
        path.unlink(missing_ok=True)
