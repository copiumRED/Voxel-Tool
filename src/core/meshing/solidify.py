from __future__ import annotations

from core.part import Part
from core.meshing.greedy_mesher import extract_greedy_surface_mesh
from core.meshing.mesh import SurfaceMesh
from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def build_solid_mesh(voxels: VoxelGrid, *, greedy: bool = True) -> SurfaceMesh:
    if greedy:
        return extract_greedy_surface_mesh(voxels)
    return extract_surface_mesh(voxels)


def rebuild_part_mesh(part: Part, *, greedy: bool = True) -> SurfaceMesh:
    if part.mesh_cache is not None and part.dirty_bounds is not None:
        dirty_bounds = _expand_bounds(part.dirty_bounds, pad=1)
        if _bounds_volume(dirty_bounds) <= 4096:
            mesh = _incremental_rebuild(part, dirty_bounds, greedy=greedy)
            part.mesh_cache = mesh
            part.dirty_bounds = None
            return mesh
    mesh = build_solid_mesh(part.voxels, greedy=greedy)
    part.mesh_cache = mesh
    part.dirty_bounds = None
    return mesh


def _incremental_rebuild(part: Part, dirty_bounds: tuple[int, int, int, int, int, int], *, greedy: bool) -> SurfaceMesh:
    preserved = _mesh_without_bounds(part.mesh_cache or SurfaceMesh(), dirty_bounds)
    local_voxels = _extract_voxels_in_bounds(part.voxels, dirty_bounds)
    patch = build_solid_mesh(local_voxels, greedy=greedy)
    return _merge_meshes(preserved, patch)


def _extract_voxels_in_bounds(
    voxels: VoxelGrid,
    bounds: tuple[int, int, int, int, int, int],
) -> VoxelGrid:
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    local = VoxelGrid()
    for x, y, z, color in voxels.to_list():
        if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
            local.set(x, y, z, color)
    return local


def _mesh_without_bounds(mesh: SurfaceMesh, bounds: tuple[int, int, int, int, int, int]) -> SurfaceMesh:
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    filtered = SurfaceMesh()
    for face_index, quad in enumerate(mesh.quads):
        verts = [mesh.vertices[i] for i in quad]
        if _quad_intersects_bounds(verts, min_x, max_x, min_y, max_y, min_z, max_z):
            continue
        base = len(filtered.vertices)
        filtered.vertices.extend(verts)
        filtered.quads.append((base, base + 1, base + 2, base + 3))
        if face_index < len(mesh.face_colors):
            filtered.face_colors.append(mesh.face_colors[face_index])
        else:
            filtered.face_colors.append(0)
    return filtered


def _merge_meshes(first: SurfaceMesh, second: SurfaceMesh) -> SurfaceMesh:
    merged = SurfaceMesh(vertices=list(first.vertices), quads=list(first.quads), face_colors=list(first.face_colors))
    for face_index, quad in enumerate(second.quads):
        base = len(merged.vertices)
        verts = [second.vertices[i] for i in quad]
        merged.vertices.extend(verts)
        merged.quads.append((base, base + 1, base + 2, base + 3))
        if face_index < len(second.face_colors):
            merged.face_colors.append(second.face_colors[face_index])
        else:
            merged.face_colors.append(0)
    return merged


def _quad_intersects_bounds(
    vertices: list[tuple[float, float, float]],
    min_x: int,
    max_x: int,
    min_y: int,
    max_y: int,
    min_z: int,
    max_z: int,
) -> bool:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    return not (
        max(xs) < min_x
        or min(xs) > max_x + 1
        or max(ys) < min_y
        or min(ys) > max_y + 1
        or max(zs) < min_z
        or min(zs) > max_z + 1
    )


def _expand_bounds(bounds: tuple[int, int, int, int, int, int], *, pad: int) -> tuple[int, int, int, int, int, int]:
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    return (
        min_x - pad,
        max_x + pad,
        min_y - pad,
        max_y + pad,
        min_z - pad,
        max_z + pad,
    )


def _bounds_volume(bounds: tuple[int, int, int, int, int, int]) -> int:
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    return max(1, (max_x - min_x + 1)) * max(1, (max_y - min_y + 1)) * max(1, (max_z - min_z + 1))
