from __future__ import annotations

from dataclasses import dataclass, field

from core.meshing.solidify import build_solid_mesh
from core.part import Part
from core.project import Project


VOXEL_SIZE_METERS = 1.0


@dataclass(slots=True)
class PartStats:
    part_id: str
    part_name: str
    triangles: int
    faces: int
    edges: int
    vertices: int
    bounds_size: tuple[int, int, int]
    bounds_meters: tuple[float, float, float]
    materials_used: int
    degenerate_quads: int
    non_manifold_edge_hints: int
    incremental_rebuild_attempts: int
    incremental_rebuild_fallbacks: int
    voxel_memory_bytes: int
    mesh_memory_bytes: int
    total_memory_bytes: int


@dataclass(slots=True)
class SceneStats:
    parts: list[PartStats] = field(default_factory=list)
    triangles: int = 0
    faces: int = 0
    edges: int = 0
    vertices: int = 0
    materials_used: int = 0
    voxel_memory_bytes: int = 0
    mesh_memory_bytes: int = 0
    total_memory_bytes: int = 0


def compute_scene_stats(project: Project) -> SceneStats:
    scene_stats = SceneStats()
    scene_materials: set[int] = set()
    for part in project.scene.parts.values():
        part_stats = _compute_part_stats(part)
        scene_stats.parts.append(part_stats)
        scene_stats.triangles += part_stats.triangles
        scene_stats.faces += part_stats.faces
        scene_stats.edges += part_stats.edges
        scene_stats.vertices += part_stats.vertices
        scene_materials.update(_part_materials(part))
        scene_stats.voxel_memory_bytes += part_stats.voxel_memory_bytes
        scene_stats.mesh_memory_bytes += part_stats.mesh_memory_bytes
    scene_stats.materials_used = len(scene_materials)
    scene_stats.total_memory_bytes = scene_stats.voxel_memory_bytes + scene_stats.mesh_memory_bytes
    return scene_stats


def _compute_part_stats(part: Part) -> PartStats:
    mesh = (
        part.mesh_cache
        if part.mesh_cache is not None and part.dirty_bounds is None
        else build_solid_mesh(part.voxels, greedy=True)
    )
    unique_vertices = set(mesh.vertices)
    unique_edges: set[tuple[int, int]] = set()
    edge_use_count: dict[tuple[int, int], int] = {}
    degenerate_quads = 0
    for a, b, c, d in mesh.quads:
        quad_vertices = {a, b, c, d}
        if len(quad_vertices) < 4:
            degenerate_quads += 1
        for start, end in ((a, b), (b, c), (c, d), (d, a)):
            key = (min(start, end), max(start, end))
            unique_edges.add(key)
            edge_use_count[key] = edge_use_count.get(key, 0) + 1
    non_manifold_edge_hints = sum(1 for count in edge_use_count.values() if count > 2)
    voxel_memory_bytes = part.voxels.count() * 16
    mesh_memory_bytes = (len(mesh.vertices) * 12) + (len(mesh.quads) * 16) + (len(mesh.face_colors) * 4)
    return PartStats(
        part_id=part.part_id,
        part_name=part.name,
        triangles=mesh.face_count * 2,
        faces=mesh.face_count,
        edges=len(unique_edges),
        vertices=len(unique_vertices),
        bounds_size=_voxel_bounds_size(part),
        bounds_meters=_bounds_meters(_voxel_bounds_size(part)),
        materials_used=len(_part_materials(part)),
        degenerate_quads=degenerate_quads,
        non_manifold_edge_hints=non_manifold_edge_hints,
        incremental_rebuild_attempts=part.incremental_rebuild_attempts,
        incremental_rebuild_fallbacks=part.incremental_rebuild_fallbacks,
        voxel_memory_bytes=voxel_memory_bytes,
        mesh_memory_bytes=mesh_memory_bytes,
        total_memory_bytes=voxel_memory_bytes + mesh_memory_bytes,
    )


def _part_materials(part: Part) -> set[int]:
    return {color for _x, _y, _z, color in part.voxels.to_list()}


def _voxel_bounds_size(part: Part) -> tuple[int, int, int]:
    rows = part.voxels.to_list()
    if not rows:
        return (0, 0, 0)
    xs = [row[0] for row in rows]
    ys = [row[1] for row in rows]
    zs = [row[2] for row in rows]
    return (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(zs) - min(zs) + 1)


def _bounds_meters(bounds_size: tuple[int, int, int]) -> tuple[float, float, float]:
    bx, by, bz = bounds_size
    return (bx * VOXEL_SIZE_METERS, by * VOXEL_SIZE_METERS, bz * VOXEL_SIZE_METERS)
