from __future__ import annotations

import random

from core.meshing.solidify import build_solid_mesh, rebuild_part_mesh
from core.part import Part
from core.voxels.voxel_grid import VoxelGrid


def test_incremental_rebuild_matches_full_rebuild_for_local_edit() -> None:
    voxels = VoxelGrid()
    for x in range(3):
        for y in range(3):
            voxels.set(x, y, 0, 1)
    part = Part(part_id="p1", name="Part 1", voxels=voxels)

    rebuild_part_mesh(part, greedy=True)
    part.voxels.set(1, 1, 1, 2)
    part.mark_dirty_cells({(1, 1, 1)})
    incremental = rebuild_part_mesh(part, greedy=True)
    full = build_solid_mesh(part.voxels, greedy=True)

    assert _mesh_signature(incremental) == _mesh_signature(full)
    assert part.dirty_bounds is None


def _mesh_signature(mesh) -> set[tuple[tuple[float, float, float], ...]]:
    faces: set[tuple[tuple[float, float, float], ...]] = set()
    for quad in mesh.quads:
        verts = tuple(sorted(mesh.vertices[index] for index in quad))
        faces.add(verts)
    return faces


def test_incremental_rebuild_randomized_local_edit_sequences_match_full_rebuild() -> None:
    seeds = (7, 19, 41)
    for seed in seeds:
        rng = random.Random(seed)
        voxels = VoxelGrid()
        for _ in range(50):
            voxels.set(rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(-2, 2), rng.randint(1, 4))
        part = Part(part_id=f"p-seed-{seed}", name="Part Seed", voxels=voxels)
        rebuild_part_mesh(part, greedy=True)

        for _ in range(10):
            edits: set[tuple[int, int, int]] = set()
            for _ in range(5):
                x = rng.randint(-4, 4)
                y = rng.randint(-4, 4)
                z = rng.randint(-2, 2)
                if rng.random() < 0.5:
                    part.voxels.remove(x, y, z)
                else:
                    part.voxels.set(x, y, z, rng.randint(1, 4))
                edits.add((x, y, z))
            part.mark_dirty_cells(edits)
            incremental = rebuild_part_mesh(part, greedy=True)
            full = build_solid_mesh(part.voxels, greedy=True)
            assert _mesh_signature(incremental) == _mesh_signature(full)
