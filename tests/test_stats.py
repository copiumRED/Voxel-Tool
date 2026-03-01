from __future__ import annotations

from core.analysis.stats import compute_scene_stats
from core.meshing.mesh import SurfaceMesh
from core.meshing.solidify import rebuild_part_mesh
from core.project import Project


def test_compute_scene_stats_part_and_scene_totals() -> None:
    project = Project(name="Stats")
    part_a = project.scene.get_active_part()
    part_a.voxels.set(0, 0, 0, 1)
    part_a.voxels.set(1, 0, 0, 1)

    part_b = project.scene.add_part("Part 2")
    part_b.voxels.set(0, 0, 0, 2)
    part_b.voxels.set(0, 1, 0, 3)

    stats = compute_scene_stats(project)
    assert len(stats.parts) == 2
    assert stats.triangles > 0
    assert stats.faces > 0
    assert stats.edges > 0
    assert stats.vertices > 0
    assert stats.materials_used == 3
    assert stats.total_memory_bytes >= stats.voxel_memory_bytes
    assert stats.total_memory_bytes >= stats.mesh_memory_bytes

    first = next(part for part in stats.parts if part.part_id == part_a.part_id)
    second = next(part for part in stats.parts if part.part_id == part_b.part_id)
    assert first.bounds_size == (2, 1, 1)
    assert second.bounds_size == (1, 2, 1)
    assert first.bounds_meters == (2.0, 1.0, 1.0)
    assert second.bounds_meters == (1.0, 2.0, 1.0)
    assert first.voxel_memory_bytes == 2 * 16
    assert second.voxel_memory_bytes == 2 * 16


def test_rebuild_mesh_refreshes_stats_from_cache() -> None:
    project = Project(name="Stats Cache")
    part = project.scene.get_active_part()
    part.voxels.set(0, 0, 0, 1)

    rebuild_part_mesh(part, greedy=True)
    baseline = compute_scene_stats(project)
    assert baseline.faces > 0

    part.mesh_cache = SurfaceMesh(vertices=[], quads=[])
    stale = compute_scene_stats(project)
    assert stale.faces == 0

    rebuild_part_mesh(part, greedy=True)
    refreshed = compute_scene_stats(project)
    assert refreshed.faces == baseline.faces


def test_compute_scene_stats_reports_mesh_qa_diagnostics() -> None:
    project = Project(name="Stats QA")
    part = project.scene.get_active_part()
    part.mesh_cache = SurfaceMesh(
        vertices=[
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 1.0),
            (0.0, 0.0, 1.0),
            (1.0, 1.0, 1.0),
            (0.0, 1.0, 1.0),
        ],
        quads=[
            (0, 0, 1, 2),  # degenerate
            (0, 1, 2, 3),
            (1, 0, 4, 5),
            (0, 1, 6, 7),
        ],
        face_colors=[0, 0, 0, 0],
    )
    part.dirty_bounds = None

    stats = compute_scene_stats(project)
    current = stats.parts[0]
    assert current.degenerate_quads == 1
    assert current.non_manifold_edge_hints >= 1


def test_compute_scene_stats_memory_estimates_are_deterministic() -> None:
    project = Project(name="Stats Memory")
    part = project.scene.get_active_part()
    part.voxels.set(0, 0, 0, 1)
    part.voxels.set(1, 0, 0, 1)
    stats_a = compute_scene_stats(project)
    stats_b = compute_scene_stats(project)
    assert stats_a.total_memory_bytes == stats_b.total_memory_bytes
    assert stats_a.parts[0].total_memory_bytes == stats_b.parts[0].total_memory_bytes
