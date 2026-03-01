from __future__ import annotations

import json
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
        assert primitive["mode"] == 4
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
