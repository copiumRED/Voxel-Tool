from __future__ import annotations

from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def test_surface_extractor_single_voxel_face_count_matches_culling() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    mesh = extract_surface_mesh(voxels)
    assert mesh.face_count == 6
    assert len(mesh.vertices) == 24


def test_surface_extractor_adjacent_voxels_cull_internal_face() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    voxels.set(1, 0, 0, 2)
    mesh = extract_surface_mesh(voxels)
    assert mesh.face_count == 10
