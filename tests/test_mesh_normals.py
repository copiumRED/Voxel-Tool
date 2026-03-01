from __future__ import annotations

from core.meshing.greedy_mesher import extract_greedy_surface_mesh
from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def test_surface_mesh_normals_point_outward_for_single_voxel() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    mesh = extract_surface_mesh(voxels)
    _assert_outward_normals(mesh)


def test_greedy_mesh_normals_point_outward_for_single_voxel() -> None:
    voxels = VoxelGrid()
    voxels.set(0, 0, 0, 1)
    mesh = extract_greedy_surface_mesh(voxels)
    _assert_outward_normals(mesh)


def _assert_outward_normals(mesh) -> None:
    min_x = min(v[0] for v in mesh.vertices)
    max_x = max(v[0] for v in mesh.vertices)
    min_y = min(v[1] for v in mesh.vertices)
    max_y = max(v[1] for v in mesh.vertices)
    min_z = min(v[2] for v in mesh.vertices)
    max_z = max(v[2] for v in mesh.vertices)
    center = ((min_x + max_x) * 0.5, (min_y + max_y) * 0.5, (min_z + max_z) * 0.5)

    for idx, quad in enumerate(mesh.quads):
        nx, ny, nz = mesh.quad_normal(idx)
        ax, ay, az = mesh.vertices[quad[0]]
        bx, by, bz = mesh.vertices[quad[1]]
        cx, cy, cz = mesh.vertices[quad[2]]
        dx, dy, dz = mesh.vertices[quad[3]]
        face_center = (
            (ax + bx + cx + dx) * 0.25,
            (ay + by + cy + dy) * 0.25,
            (az + bz + cz + dz) * 0.25,
        )
        outward = (
            face_center[0] - center[0],
            face_center[1] - center[1],
            face_center[2] - center[2],
        )
        dot = (nx * outward[0]) + (ny * outward[1]) + (nz * outward[2])
        assert dot > 0.0

