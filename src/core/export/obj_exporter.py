from __future__ import annotations

from core.voxels.voxel_grid import VoxelGrid


def export_voxels_to_obj(voxels: VoxelGrid, palette: list[tuple[int, int, int]], path: str) -> None:
    # Kept for next cycle when material/color export is added.
    _ = palette

    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool naive OBJ export\n")
        rows = voxels.to_list()
        if not rows:
            file_obj.write("# No voxels to export\n")
            return

        vertex_index_offset = 1
        for x, y, z, _color_index in rows:
            # Unit cube aligned to grid, with voxel coordinate as min corner.
            verts = [
                (x, y, z),
                (x + 1, y, z),
                (x + 1, y + 1, z),
                (x, y + 1, z),
                (x, y, z + 1),
                (x + 1, y, z + 1),
                (x + 1, y + 1, z + 1),
                (x, y + 1, z + 1),
            ]
            for vx, vy, vz in verts:
                file_obj.write(f"v {vx} {vy} {vz}\n")

            faces = [
                (1, 4, 3, 2),  # -Z
                (5, 6, 7, 8),  # +Z
                (1, 2, 6, 5),  # -Y
                (2, 3, 7, 6),  # +X
                (3, 4, 8, 7),  # +Y
                (4, 1, 5, 8),  # -X
            ]
            for a, b, c, d in faces:
                file_obj.write(
                    f"f {vertex_index_offset + a - 1} {vertex_index_offset + b - 1} "
                    f"{vertex_index_offset + c - 1} {vertex_index_offset + d - 1}\n"
                )

            vertex_index_offset += 8
