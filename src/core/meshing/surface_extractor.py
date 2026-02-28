from __future__ import annotations

from core.meshing.mesh import SurfaceMesh
from core.voxels.voxel_grid import VoxelGrid


def extract_surface_mesh(voxels: VoxelGrid) -> SurfaceMesh:
    mesh = SurfaceMesh()
    rows = voxels.to_list()
    if not rows:
        return mesh

    occupied = {(x, y, z) for x, y, z, _color_index in rows}
    for x, y, z, color_index in rows:
        face_defs = [
            ((0, 0, -1), [(x, y, z), (x, y + 1, z), (x + 1, y + 1, z), (x + 1, y, z)]),  # -Z
            (
                (0, 0, 1),
                [(x, y, z + 1), (x + 1, y, z + 1), (x + 1, y + 1, z + 1), (x, y + 1, z + 1)],
            ),  # +Z
            ((0, -1, 0), [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1)]),  # -Y
            (
                (1, 0, 0),
                [(x + 1, y, z), (x + 1, y + 1, z), (x + 1, y + 1, z + 1), (x + 1, y, z + 1)],
            ),  # +X
            (
                (0, 1, 0),
                [(x + 1, y + 1, z), (x, y + 1, z), (x, y + 1, z + 1), (x + 1, y + 1, z + 1)],
            ),  # +Y
            ((-1, 0, 0), [(x, y + 1, z), (x, y, z), (x, y, z + 1), (x, y + 1, z + 1)]),  # -X
        ]
        for (dx, dy, dz), face_verts in face_defs:
            if (x + dx, y + dy, z + dz) in occupied:
                continue
            base = len(mesh.vertices)
            for vx, vy, vz in face_verts:
                mesh.vertices.append((float(vx), float(vy), float(vz)))
            mesh.quads.append((base, base + 1, base + 2, base + 3))
            mesh.face_colors.append(color_index)
    return mesh
