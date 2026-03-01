from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

from core.meshing.mesh import SurfaceMesh
from core.meshing.solidify import build_solid_mesh
from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class ObjExportOptions:
    use_greedy_mesh: bool = True
    triangulate: bool = False
    scale_factor: float = 1.0
    pivot_mode: str = "none"
    write_mtl: bool = True


def export_voxels_to_obj(
    voxels: VoxelGrid,
    palette: list[tuple[int, int, int]],
    path: str,
    options: ObjExportOptions | None = None,
    mesh: SurfaceMesh | None = None,
) -> None:
    export_options = options or ObjExportOptions()
    export_mesh = mesh or build_solid_mesh(voxels, greedy=export_options.use_greedy_mesh)
    transformed_vertices = _transform_vertices(
        export_mesh.vertices,
        pivot_mode=export_options.pivot_mode,
        scale_factor=export_options.scale_factor,
    )

    mtl_name = ""
    if export_options.write_mtl and export_mesh.face_count > 0:
        mtl_name = f"{Path(path).stem}.mtl"
        _write_mtl_file(Path(path).with_suffix(".mtl"), palette)

    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool OBJ export\n")
        if export_mesh.face_count == 0:
            file_obj.write("# No voxels to export\n")
            return
        if mtl_name:
            file_obj.write(f"mtllib {mtl_name}\n")
            file_obj.write("usemtl voxel_default\n")

        for vx, vy, vz in transformed_vertices:
            file_obj.write(f"v {vx} {vy} {vz}\n")
        for a, b, c, d in export_mesh.quads:
            if export_options.triangulate:
                file_obj.write(f"f {a + 1} {b + 1} {c + 1}\n")
                file_obj.write(f"f {a + 1} {c + 1} {d + 1}\n")
            else:
                file_obj.write(f"f {a + 1} {b + 1} {c + 1} {d + 1}\n")


def _transform_vertices(
    vertices: list[tuple[float, float, float]],
    *,
    pivot_mode: str,
    scale_factor: float,
) -> list[tuple[float, float, float]]:
    if not vertices:
        return []
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    mode = pivot_mode.strip().lower()
    if mode == "center":
        pivot = ((min_x + max_x) * 0.5, (min_y + max_y) * 0.5, (min_z + max_z) * 0.5)
    elif mode == "bottom":
        pivot = ((min_x + max_x) * 0.5, min_y, (min_z + max_z) * 0.5)
    else:
        pivot = (0.0, 0.0, 0.0)

    scale = float(scale_factor)
    return [((x - pivot[0]) * scale, (y - pivot[1]) * scale, (z - pivot[2]) * scale) for x, y, z in vertices]


def _write_mtl_file(path: Path, palette: list[tuple[int, int, int]]) -> None:
    if palette:
        r, g, b = palette[0]
    else:
        r, g, b = 200, 200, 200
    kd = (float(r) / 255.0, float(g) / 255.0, float(b) / 255.0)
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool MTL export\n")
        file_obj.write("newmtl voxel_default\n")
        file_obj.write(f"Kd {kd[0]} {kd[1]} {kd[2]}\n")
