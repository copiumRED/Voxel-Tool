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
