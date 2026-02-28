from __future__ import annotations

import uuid

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
