from __future__ import annotations

from dataclasses import dataclass

from core.meshing.solidify import build_solid_mesh
from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class ObjExportOptions:
    use_greedy_mesh: bool = True
    triangulate: bool = False


def export_voxels_to_obj(
    voxels: VoxelGrid,
    palette: list[tuple[int, int, int]],
    path: str,
    options: ObjExportOptions | None = None,
) -> None:
    # Reserved for future palette/material output.
    _ = palette
    export_options = options or ObjExportOptions()
    mesh = build_solid_mesh(voxels, greedy=export_options.use_greedy_mesh)

    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool OBJ export\n")
        if mesh.face_count == 0:
            file_obj.write("# No voxels to export\n")
            return

        for vx, vy, vz in mesh.vertices:
            file_obj.write(f"v {vx} {vy} {vz}\n")
        for a, b, c, d in mesh.quads:
            if export_options.triangulate:
                file_obj.write(f"f {a + 1} {b + 1} {c + 1}\n")
                file_obj.write(f"f {a + 1} {c + 1} {d + 1}\n")
            else:
                file_obj.write(f"f {a + 1} {b + 1} {c + 1} {d + 1}\n")
