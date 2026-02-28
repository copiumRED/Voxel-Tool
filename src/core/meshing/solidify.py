from __future__ import annotations

from core.meshing.greedy_mesher import extract_greedy_surface_mesh
from core.meshing.mesh import SurfaceMesh
from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def build_solid_mesh(voxels: VoxelGrid, *, greedy: bool = True) -> SurfaceMesh:
    if greedy:
        return extract_greedy_surface_mesh(voxels)
    return extract_surface_mesh(voxels)
