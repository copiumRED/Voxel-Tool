from __future__ import annotations

from core.meshing.greedy_mesher import extract_greedy_surface_mesh
from core.meshing.solidify import build_solid_mesh
from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def test_greedy_mesher_reduces_faces_for_rectangular_block() -> None:
    voxels = VoxelGrid()
    for x in range(2):
        voxels.set(x, 0, 0, 1)

    naive = extract_surface_mesh(voxels)
    greedy = extract_greedy_surface_mesh(voxels)
    assert greedy.face_count < naive.face_count
    assert greedy.face_count == 6
    assert naive.face_count == 10


def test_solidify_builder_switches_between_naive_and_greedy() -> None:
    voxels = VoxelGrid()
    for x in range(3):
        for y in range(2):
            voxels.set(x, y, 0, 2)

    naive = build_solid_mesh(voxels, greedy=False)
    greedy = build_solid_mesh(voxels, greedy=True)
    assert greedy.face_count < naive.face_count
