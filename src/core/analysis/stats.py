from __future__ import annotations

from dataclasses import dataclass, field

from core.meshing.solidify import build_solid_mesh
from core.part import Part
from core.project import Project


@dataclass(slots=True)
class PartStats:
    part_id: str
    part_name: str
    triangles: int
    faces: int
    edges: int
    vertices: int
    bounds_size: tuple[int, int, int]
    materials_used: int


@dataclass(slots=True)
class SceneStats:
    parts: list[PartStats] = field(default_factory=list)
    triangles: int = 0
    faces: int = 0
    edges: int = 0
    vertices: int = 0
    materials_used: int = 0


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
    scene_stats.materials_used = len(scene_materials)
    return scene_stats


def _compute_part_stats(part: Part) -> PartStats:
    mesh = part.mesh_cache if part.mesh_cache is not None else build_solid_mesh(part.voxels, greedy=True)
    unique_vertices = set(mesh.vertices)
    unique_edges: set[tuple[int, int]] = set()
    for a, b, c, d in mesh.quads:
        for start, end in ((a, b), (b, c), (c, d), (d, a)):
            unique_edges.add((min(start, end), max(start, end)))
    return PartStats(
        part_id=part.part_id,
        part_name=part.name,
        triangles=mesh.face_count * 2,
        faces=mesh.face_count,
        edges=len(unique_edges),
        vertices=len(unique_vertices),
        bounds_size=_voxel_bounds_size(part),
        materials_used=len(_part_materials(part)),
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
