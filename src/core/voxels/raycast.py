from __future__ import annotations

from math import floor, sqrt

from core.voxels.voxel_grid import VoxelGrid


def raycast_voxel_surface(
    voxels: VoxelGrid,
    origin: tuple[float, float, float],
    direction: tuple[float, float, float],
    *,
    max_distance: float = 200.0,
    step_size: float = 0.1,
) -> tuple[tuple[int, int, int], tuple[int, int, int] | None] | None:
    dx, dy, dz = direction
    length = sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return None
    ndx, ndy, ndz = dx / length, dy / length, dz / length

    previous_cell: tuple[int, int, int] | None = None
    visited: set[tuple[int, int, int]] = set()
    t = 0.0
    while t <= max_distance:
        px = origin[0] + ndx * t
        py = origin[1] + ndy * t
        pz = origin[2] + ndz * t
        cell = (
            int(floor(px + 0.5)),
            int(floor(py + 0.5)),
            int(floor(pz + 0.5)),
        )
        if cell not in visited:
            visited.add(cell)
            if voxels.get(cell[0], cell[1], cell[2]) is not None:
                return cell, previous_cell
            previous_cell = cell
        t += step_size
    return None
