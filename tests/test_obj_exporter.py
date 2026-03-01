from __future__ import annotations

import uuid
from pathlib import Path

from core.meshing.mesh import SurfaceMesh
from core.export.obj_exporter import ObjExportOptions, export_voxels_to_obj
from core.palette import DEFAULT_PALETTE
from core.voxels.voxel_grid import VoxelGrid
from util.fs import get_app_temp_dir


def _count_prefixed_lines(path, prefix: str) -> int:
    with open(path, "r", encoding="utf-8") as file_obj:
        return sum(1 for line in file_obj if line.startswith(prefix))


def test_export_obj_single_voxel_counts() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    path = get_app_temp_dir("VoxelTool") / f"obj-export-one-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(voxels, list(DEFAULT_PALETTE), str(path))
        assert path.exists()
        assert _count_prefixed_lines(path, "f ") == 6
    finally:
        path.unlink(missing_ok=True)


def test_export_obj_two_adjacent_voxels_face_culling() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(1, 0, 0, 1)
    path = get_app_temp_dir("VoxelTool") / f"obj-export-two-adj-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(
            voxels,
            list(DEFAULT_PALETTE),
            str(path),
            options=ObjExportOptions(use_greedy_mesh=False),
        )
        assert path.exists()
        assert _count_prefixed_lines(path, "f ") == 10
    finally:
        path.unlink(missing_ok=True)


def test_export_obj_two_non_adjacent_voxels_faces() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(2, 0, 0, 1)
    path = get_app_temp_dir("VoxelTool") / f"obj-export-two-sep-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(
            voxels,
            list(DEFAULT_PALETTE),
            str(path),
            options=ObjExportOptions(use_greedy_mesh=False),
        )
        assert path.exists()
        assert _count_prefixed_lines(path, "f ") == 12
    finally:
        path.unlink(missing_ok=True)


def test_export_obj_greedy_reduces_adjacent_faces() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    voxels.set(1, 0, 0, 0)
    path = get_app_temp_dir("VoxelTool") / f"obj-export-greedy-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(voxels, list(DEFAULT_PALETTE), str(path), options=ObjExportOptions(use_greedy_mesh=True))
        assert path.exists()
        assert _count_prefixed_lines(path, "f ") == 6
    finally:
        path.unlink(missing_ok=True)


def test_export_obj_uses_provided_mesh_buffer() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    mesh = SurfaceMesh(vertices=[(0.0, 0.0, 0.0)], quads=[])
    path = get_app_temp_dir("VoxelTool") / f"obj-export-mesh-buffer-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(
            voxels,
            list(DEFAULT_PALETTE),
            str(path),
            options=ObjExportOptions(use_greedy_mesh=True),
            mesh=mesh,
        )
        content = path.read_text(encoding="utf-8")
        assert "# No voxels to export" in content
    finally:
        path.unlink(missing_ok=True)


def test_export_obj_writes_mtl_and_material_reference() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 0)
    path = get_app_temp_dir("VoxelTool") / f"obj-export-mtl-{uuid.uuid4().hex}.obj"
    mtl_path = path.with_suffix(".mtl")
    try:
        export_voxels_to_obj(voxels, list(DEFAULT_PALETTE), str(path))
        text = path.read_text(encoding="utf-8")
        assert "mtllib" in text
        assert "usemtl voxel_default" in text
        assert mtl_path.exists()
    finally:
        path.unlink(missing_ok=True)
        mtl_path.unlink(missing_ok=True)


def test_export_obj_applies_scale_and_center_pivot() -> None:
    mesh = SurfaceMesh(
        vertices=[
            (1.0, 0.0, 1.0),
            (3.0, 0.0, 1.0),
            (3.0, 0.0, 3.0),
            (1.0, 0.0, 3.0),
        ],
        quads=[(0, 1, 2, 3)],
    )
    path = get_app_temp_dir("VoxelTool") / f"obj-export-scale-pivot-{uuid.uuid4().hex}.obj"
    try:
        export_voxels_to_obj(
            VoxelGrid(),
            list(DEFAULT_PALETTE),
            str(path),
            options=ObjExportOptions(scale_factor=2.0, pivot_mode="center"),
            mesh=mesh,
        )
        vertices = _read_vertices(path)
        assert (-2.0, 0.0, -2.0) in vertices
        assert (2.0, 0.0, 2.0) in vertices
    finally:
        path.unlink(missing_ok=True)
        path.with_suffix(".mtl").unlink(missing_ok=True)


def _read_vertices(path: Path) -> list[tuple[float, float, float]]:
    vertices: list[tuple[float, float, float]] = []
    with open(path, "r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.startswith("v "):
                _, x, y, z = line.strip().split(" ")
                vertices.append((float(x), float(y), float(z)))
    return vertices
