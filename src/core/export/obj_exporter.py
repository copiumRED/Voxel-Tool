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

        occupied = {(x, y, z) for x, y, z, _color_index in rows}
        vertex_index_offset = 1
        for x, y, z, _color_index in rows:
            # Unit cube aligned to grid, with voxel coordinate as min corner.
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
                for vx, vy, vz in face_verts:
                    file_obj.write(f"v {vx} {vy} {vz}\n")
                file_obj.write(
                    f"f {vertex_index_offset} {vertex_index_offset + 1} "
                    f"{vertex_index_offset + 2} {vertex_index_offset + 3}\n"
                )
                vertex_index_offset += 4
