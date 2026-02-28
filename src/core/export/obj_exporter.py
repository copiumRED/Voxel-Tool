from __future__ import annotations

from core.meshing.surface_extractor import extract_surface_mesh
from core.voxels.voxel_grid import VoxelGrid


def export_voxels_to_obj(voxels: VoxelGrid, palette: list[tuple[int, int, int]], path: str) -> None:
    # Kept for next cycle when material/color export is added.
    _ = palette

    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool naive OBJ export\n")
        mesh = extract_surface_mesh(voxels)
        if mesh.face_count == 0:
            file_obj.write("# No voxels to export\n")
            return

        for vx, vy, vz in mesh.vertices:
            file_obj.write(f"v {vx} {vy} {vz}\n")
        for a, b, c, d in mesh.quads:
            file_obj.write(f"f {a + 1} {b + 1} {c + 1} {d + 1}\n")
