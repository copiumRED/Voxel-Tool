from __future__ import annotations

from collections import defaultdict

from core.meshing.mesh import SurfaceMesh
from core.voxels.voxel_grid import VoxelGrid


def extract_greedy_surface_mesh(voxels: VoxelGrid) -> SurfaceMesh:
    mesh = SurfaceMesh()
    rows = voxels.to_list()
    if not rows:
        return mesh

    occupied = {(x, y, z): color for x, y, z, color in rows}
    groups: dict[tuple[str, int, int, int], set[tuple[int, int]]] = defaultdict(set)

    for (x, y, z), color in occupied.items():
        if (x + 1, y, z) not in occupied:
            groups[("x", 1, x + 1, color)].add((y, z))
        if (x - 1, y, z) not in occupied:
            groups[("x", -1, x, color)].add((y, z))
        if (x, y + 1, z) not in occupied:
            groups[("y", 1, y + 1, color)].add((x, z))
        if (x, y - 1, z) not in occupied:
            groups[("y", -1, y, color)].add((x, z))
        if (x, y, z + 1) not in occupied:
            groups[("z", 1, z + 1, color)].add((x, y))
        if (x, y, z - 1) not in occupied:
            groups[("z", -1, z, color)].add((x, y))

    for (axis, sign, plane, color), cells in groups.items():
        for u0, v0, u1, v1 in _greedy_rectangles(cells):
            quad = _quad_from_rect(axis, sign, plane, u0, v0, u1, v1)
            base = len(mesh.vertices)
            mesh.vertices.extend(quad)
            mesh.quads.append((base, base + 1, base + 2, base + 3))
            mesh.face_colors.append(color)

    return mesh


def _greedy_rectangles(cells: set[tuple[int, int]]) -> list[tuple[int, int, int, int]]:
    pending = set(cells)
    rectangles: list[tuple[int, int, int, int]] = []
    while pending:
        u0, v0 = min(pending)
        width = 1
        while (u0 + width, v0) in pending:
            width += 1

        height = 1
        while True:
            next_row = v0 + height
            if any((u, next_row) not in pending for u in range(u0, u0 + width)):
                break
            height += 1

        for v in range(v0, v0 + height):
            for u in range(u0, u0 + width):
                pending.remove((u, v))

        rectangles.append((u0, v0, u0 + width, v0 + height))
    return rectangles


def _quad_from_rect(
    axis: str,
    sign: int,
    plane: int,
    u0: int,
    v0: int,
    u1: int,
    v1: int,
) -> list[tuple[float, float, float]]:
    if axis == "x":
        if sign > 0:
            return [
                (float(plane), float(u0), float(v0)),
                (float(plane), float(u1), float(v0)),
                (float(plane), float(u1), float(v1)),
                (float(plane), float(u0), float(v1)),
            ]
        return [
            (float(plane), float(u0), float(v1)),
            (float(plane), float(u1), float(v1)),
            (float(plane), float(u1), float(v0)),
            (float(plane), float(u0), float(v0)),
        ]
    if axis == "y":
        if sign > 0:
            return [
                (float(u1), float(plane), float(v0)),
                (float(u0), float(plane), float(v0)),
                (float(u0), float(plane), float(v1)),
                (float(u1), float(plane), float(v1)),
            ]
        return [
            (float(u0), float(plane), float(v0)),
            (float(u1), float(plane), float(v0)),
            (float(u1), float(plane), float(v1)),
            (float(u0), float(plane), float(v1)),
        ]
    if sign > 0:
        return [
            (float(u0), float(v0), float(plane)),
            (float(u1), float(v0), float(plane)),
            (float(u1), float(v1), float(plane)),
            (float(u0), float(v1), float(plane)),
        ]
    return [
        (float(u1), float(v0), float(plane)),
        (float(u0), float(v0), float(plane)),
        (float(u0), float(v1), float(plane)),
        (float(u1), float(v1), float(plane)),
    ]
