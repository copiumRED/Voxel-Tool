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
    write_uvs: bool = True
    write_vertex_colors: bool = True
    vertex_color_policy: str = "first_face"
    multi_material_by_color: bool = False


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
    vertex_colors = _build_vertex_color_map(
        export_mesh,
        palette,
        policy=export_options.vertex_color_policy,
    )

    mtl_name = ""
    used_color_indices = _used_face_color_indices(export_mesh, palette)
    if export_options.write_mtl and export_mesh.face_count > 0:
        mtl_name = f"{Path(path).stem}.mtl"
        if export_options.multi_material_by_color:
            _write_mtl_file(Path(path).with_suffix(".mtl"), palette, used_color_indices=used_color_indices)
        else:
            _write_mtl_file(Path(path).with_suffix(".mtl"), palette, used_color_indices={0})

    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool OBJ export\n")
        if export_mesh.face_count == 0:
            file_obj.write("# No voxels to export\n")
            return
        if mtl_name:
            file_obj.write(f"mtllib {mtl_name}\n")
            if not export_options.multi_material_by_color:
                file_obj.write("usemtl voxel_default\n")

        for index, (vx, vy, vz) in enumerate(transformed_vertices):
            if export_options.write_vertex_colors and index in vertex_colors:
                r, g, b = vertex_colors[index]
                file_obj.write(f"v {vx} {vy} {vz} {r} {g} {b}\n")
            else:
                file_obj.write(f"v {vx} {vy} {vz}\n")

        quad_uv_indices: list[tuple[int, int, int, int]] = []
        if export_options.write_uvs:
            for _ in export_mesh.quads:
                base = len(quad_uv_indices) * 4
                file_obj.write("vt 0.0 0.0\n")
                file_obj.write("vt 1.0 0.0\n")
                file_obj.write("vt 1.0 1.0\n")
                file_obj.write("vt 0.0 1.0\n")
                quad_uv_indices.append((base + 1, base + 2, base + 3, base + 4))

        current_material: str | None = None
        for face_index, (a, b, c, d) in enumerate(export_mesh.quads):
            if mtl_name and export_options.multi_material_by_color:
                color_index = 0
                if face_index < len(export_mesh.face_colors):
                    color_index = int(export_mesh.face_colors[face_index]) % len(palette)
                material_name = _material_name(color_index)
                if material_name != current_material:
                    file_obj.write(f"usemtl {material_name}\n")
                    current_material = material_name
            uv = quad_uv_indices[face_index] if export_options.write_uvs else None
            if export_options.triangulate:
                if uv is not None:
                    file_obj.write(f"f {a + 1}/{uv[0]} {b + 1}/{uv[1]} {c + 1}/{uv[2]}\n")
                    file_obj.write(f"f {a + 1}/{uv[0]} {c + 1}/{uv[2]} {d + 1}/{uv[3]}\n")
                else:
                    file_obj.write(f"f {a + 1} {b + 1} {c + 1}\n")
                    file_obj.write(f"f {a + 1} {c + 1} {d + 1}\n")
            else:
                if uv is not None:
                    file_obj.write(f"f {a + 1}/{uv[0]} {b + 1}/{uv[1]} {c + 1}/{uv[2]} {d + 1}/{uv[3]}\n")
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


def _write_mtl_file(
    path: Path,
    palette: list[tuple[int, int, int]],
    *,
    used_color_indices: set[int],
) -> None:
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("# VoxelTool MTL export\n")
        if not used_color_indices:
            used_color_indices = {0}
        for color_index in sorted(used_color_indices):
            if palette:
                r, g, b = palette[color_index % len(palette)]
            else:
                r, g, b = 200, 200, 200
            kd = (float(r) / 255.0, float(g) / 255.0, float(b) / 255.0)
            file_obj.write(f"newmtl {_material_name(color_index)}\n")
            file_obj.write(f"Kd {kd[0]} {kd[1]} {kd[2]}\n")


def _used_face_color_indices(mesh: SurfaceMesh, palette: list[tuple[int, int, int]]) -> set[int]:
    if not palette:
        return {0}
    used: set[int] = set()
    for color_index in mesh.face_colors:
        used.add(int(color_index) % len(palette))
    if not used:
        used.add(0)
    return used


def _material_name(color_index: int) -> str:
    if int(color_index) == 0:
        return "voxel_default"
    return f"voxel_color_{int(color_index)}"


def _build_vertex_color_map(
    mesh: SurfaceMesh,
    palette: list[tuple[int, int, int]],
    *,
    policy: str = "first_face",
) -> dict[int, tuple[float, float, float]]:
    if not palette:
        return {}
    normalized_policy = policy.strip().lower()
    if normalized_policy not in {"first_face", "last_face"}:
        raise ValueError(f"Unsupported vertex color policy: {policy}")
    colors: dict[int, tuple[float, float, float]] = {}
    for face_index, quad in enumerate(mesh.quads):
        color_index = 0
        if face_index < len(mesh.face_colors):
            color_index = int(mesh.face_colors[face_index]) % len(palette)
        r, g, b = palette[color_index]
        rgb = (float(r) / 255.0, float(g) / 255.0, float(b) / 255.0)
        for vertex_index in quad:
            if normalized_policy == "first_face" and vertex_index in colors:
                continue
            if normalized_policy == "last_face" and vertex_index in colors:
                colors[vertex_index] = rgb
                continue
            if vertex_index not in colors:
                colors[vertex_index] = rgb
    return colors
