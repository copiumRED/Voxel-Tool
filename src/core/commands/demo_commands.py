from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from core.commands.command import Command
from core.voxels.voxel_grid import VoxelGrid


class RenameProjectCommand(Command):
    def __init__(self, new_name: str) -> None:
        self.new_name = new_name
        self._old_name: str | None = None

    @property
    def name(self) -> str:
        return "Rename Project"

    def do(self, ctx) -> None:
        if self._old_name is None:
            self._old_name = ctx.current_project.name
        ctx.current_project.name = self.new_name

    def undo(self, ctx) -> None:
        if self._old_name is None:
            return
        ctx.current_project.name = self._old_name


class PaintVoxelCommand(Command):
    def __init__(self, x: int, y: int, z: int, color_index: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.color_index = color_index
        self._deltas: list[_VoxelDelta] = []

    @property
    def name(self) -> str:
        return "Paint Voxel"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        brush_size = int(getattr(ctx, "brush_size", 1))
        brush_shape = str(getattr(ctx, "brush_shape", "cube"))
        base_cells = build_brush_cells((self.x, self.y, self.z), brush_size=brush_size, brush_shape=brush_shape)
        cells = _expand_mirror_cells(ctx, base_cells)
        _invalidate_active_mesh_cache(ctx, cells)
        self._deltas = _apply_voxel_mode(voxels, cells, mode="paint", color_index=self.color_index)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


class RemoveVoxelCommand(Command):
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self._deltas: list[_VoxelDelta] = []

    @property
    def name(self) -> str:
        return "Erase Voxel"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        brush_size = int(getattr(ctx, "brush_size", 1))
        brush_shape = str(getattr(ctx, "brush_shape", "cube"))
        base_cells = build_brush_cells((self.x, self.y, self.z), brush_size=brush_size, brush_shape=brush_shape)
        cells = _expand_mirror_cells(ctx, base_cells)
        _invalidate_active_mesh_cache(ctx, cells)
        self._deltas = _apply_voxel_mode(voxels, cells, mode="erase", color_index=None)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


class ClearVoxelsCommand(Command):
    def __init__(self) -> None:
        self._snapshot: list[list[int]] = []

    @property
    def name(self) -> str:
        return "Clear Voxels"

    def do(self, ctx) -> None:
        _invalidate_active_mesh_cache(ctx)
        self._snapshot = ctx.current_project.voxels.to_list()
        ctx.current_project.voxels.clear()

    def undo(self, ctx) -> None:
        ctx.current_project.voxels = VoxelGrid.from_list(self._snapshot)


class CreateTestVoxelsCommand(Command):
    def __init__(self, center_color_index: int, arm_color_index: int | None = None) -> None:
        self.center_color_index = center_color_index
        self.arm_color_index = arm_color_index if arm_color_index is not None else center_color_index
        self._snapshot: list[list[int]] = []

    @property
    def name(self) -> str:
        return "Create Test Voxels"

    def do(self, ctx) -> None:
        _invalidate_active_mesh_cache(ctx)
        self._snapshot = ctx.current_project.voxels.to_list()
        voxels = ctx.current_project.voxels
        voxels.clear()

        voxels.set(0, 0, 0, self.center_color_index)
        for x, y, z in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            voxels.set(x, y, z, self.arm_color_index)

    def undo(self, ctx) -> None:
        ctx.current_project.voxels = VoxelGrid.from_list(self._snapshot)


# Backward-compatible names retained while call sites migrate to paint/erase wording.
class AddVoxelCommand(PaintVoxelCommand):
    @property
    def name(self) -> str:
        return "Add Voxel"


@dataclass(slots=True)
class _VoxelDelta:
    x: int
    y: int
    z: int
    previous_color: int | None


class BoxVoxelCommand(Command):
    def __init__(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        z: int,
        mode: str,
        color_index: int | None = None,
    ) -> None:
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.z = z
        self.mode = mode
        self.color_index = color_index
        self._deltas: list[_VoxelDelta] = []

    @property
    def name(self) -> str:
        return "Box Fill" if self.mode == "paint" else "Box Erase"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        base_cells = build_box_plane_cells(self.start_x, self.start_y, self.end_x, self.end_y, self.z)

        cells = _expand_mirror_cells(ctx, base_cells)
        _invalidate_active_mesh_cache(ctx, cells)
        self._deltas = _apply_voxel_mode(voxels, cells, mode=self.mode, color_index=self.color_index)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


class LineVoxelCommand(Command):
    def __init__(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        z: int,
        mode: str,
        color_index: int | None = None,
    ) -> None:
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.z = z
        self.mode = mode
        self.color_index = color_index
        self._deltas: list[_VoxelDelta] = []

    @property
    def name(self) -> str:
        return "Line Paint" if self.mode == "paint" else "Line Erase"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        base_cells = build_line_plane_cells(self.start_x, self.start_y, self.end_x, self.end_y, self.z)
        cells = _expand_mirror_cells(ctx, base_cells)
        _invalidate_active_mesh_cache(ctx, cells)
        self._deltas = _apply_voxel_mode(voxels, cells, mode=self.mode, color_index=self.color_index)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


class FillVoxelCommand(Command):
    def __init__(self, x: int, y: int, z: int, mode: str, color_index: int | None = None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.mode = mode
        self.color_index = color_index
        self._deltas: list[_VoxelDelta] = []
        self.aborted_by_threshold = False
        self.aborted_threshold_limit = 0

    @property
    def name(self) -> str:
        return "Flood Fill" if self.mode == "paint" else "Flood Erase"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        self.aborted_by_threshold = False
        self.aborted_threshold_limit = 0
        target_color = voxels.get(self.x, self.y, self.z)
        if self.mode == "paint":
            if self.color_index is None:
                raise ValueError("Flood fill paint requires a color index.")
            if target_color == self.color_index:
                self._deltas = []
                return
        elif target_color is None:
            self._deltas = []
            return

        fill_mode = str(getattr(ctx, "fill_connectivity", "plane")).strip().lower()
        max_cells = int(getattr(ctx, "fill_max_cells", 5000))
        if fill_mode == "volume":
            bounds3d = _volume_fill_bounds(voxels, self.x, self.y, self.z)
            connected3d = _flood_volume_region(
                voxels,
                self.x,
                self.y,
                self.z,
                target_color,
                bounds3d,
                max_cells=max_cells,
            )
            if connected3d is None:
                self.aborted_by_threshold = True
                self.aborted_threshold_limit = max_cells
                self._deltas = []
                return
            base_cells = connected3d
        else:
            bounds = _plane_fill_bounds(voxels, self.z, self.x, self.y)
            connected = _flood_plane_region(
                voxels,
                self.x,
                self.y,
                self.z,
                target_color,
                bounds,
                max_cells=max_cells,
            )
            if connected is None:
                self.aborted_by_threshold = True
                self.aborted_threshold_limit = max_cells
                self._deltas = []
                return
            base_cells = {(x, y, self.z) for x, y in connected}
        cells = _expand_mirror_cells(ctx, base_cells)
        _invalidate_active_mesh_cache(ctx, cells)
        self._deltas = _apply_voxel_mode(voxels, cells, mode=self.mode, color_index=self.color_index)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


class MoveSelectedVoxelsCommand(Command):
    def __init__(self, selected_cells: set[tuple[int, int, int]], dx: int, dy: int, dz: int) -> None:
        self.selected_cells = {tuple(cell) for cell in selected_cells}
        self.dx = int(dx)
        self.dy = int(dy)
        self.dz = int(dz)
        self._source_colors: dict[tuple[int, int, int], int] = {}
        self._target_colors: dict[tuple[int, int, int], int] = {}
        self.moved_count = 0
        self.collision_blocked = False

    @property
    def name(self) -> str:
        return "Move Selected Voxels"

    def do(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        self._source_colors = {}
        self._target_colors = {}
        self.moved_count = 0
        self.collision_blocked = False

        for x, y, z in sorted(self.selected_cells):
            color = voxels.get(x, y, z)
            if color is not None:
                self._source_colors[(x, y, z)] = color
        if not self._source_colors:
            return

        source_cells = set(self._source_colors.keys())
        for (x, y, z), color in self._source_colors.items():
            target = (x + self.dx, y + self.dy, z + self.dz)
            self._target_colors[target] = color

        for target in self._target_colors:
            if target in source_cells:
                continue
            if voxels.get(*target) is not None:
                self.collision_blocked = True
                self._source_colors = {}
                self._target_colors = {}
                return

        _invalidate_active_mesh_cache(ctx, source_cells | set(self._target_colors.keys()))
        for source in source_cells:
            voxels.remove(*source)
        for target, color in self._target_colors.items():
            voxels.set(target[0], target[1], target[2], color)
        ctx.set_selected_voxels(set(self._target_colors.keys()))
        self.moved_count = len(self._target_colors)

    def undo(self, ctx) -> None:
        if not self._source_colors or not self._target_colors:
            return
        voxels = ctx.current_project.voxels
        _invalidate_active_mesh_cache(ctx, set(self._source_colors.keys()) | set(self._target_colors.keys()))
        for target in self._target_colors:
            voxels.remove(*target)
        for source, color in self._source_colors.items():
            voxels.set(source[0], source[1], source[2], color)
        ctx.set_selected_voxels(set(self._source_colors.keys()))


def rasterize_brush_stroke_segment(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
) -> list[tuple[int, int, int]]:
    x0, y0, z0 = start
    x1, y1, z1 = end
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0
    steps = max(abs(dx), abs(dy), abs(dz))
    if steps == 0:
        return [start]

    cells: list[tuple[int, int, int]] = []
    for step in range(steps + 1):
        t = step / steps
        x = int(round(x0 + dx * t))
        y = int(round(y0 + dy * t))
        z = int(round(z0 + dz * t))
        cell = (x, y, z)
        if not cells or cells[-1] != cell:
            cells.append(cell)
    return cells


def build_brush_cells(
    center: tuple[int, int, int],
    *,
    brush_size: int,
    brush_shape: str,
) -> set[tuple[int, int, int]]:
    x, y, z = center
    size = max(1, min(int(brush_size), 3))
    radius = size - 1
    if radius == 0:
        return {(x, y, z)}

    shape = brush_shape.strip().lower()
    if shape not in {"cube", "sphere"}:
        shape = "cube"

    cells: set[tuple[int, int, int]] = set()
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if shape == "sphere" and sqrt((dx * dx) + (dy * dy) + (dz * dz)) > radius:
                    continue
                cells.add((x + dx, y + dy, z + dz))
    return cells


def build_box_plane_cells(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    z: int,
) -> set[tuple[int, int, int]]:
    cells: set[tuple[int, int, int]] = set()
    min_x, max_x = sorted((start_x, end_x))
    min_y, max_y = sorted((start_y, end_y))
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            cells.add((x, y, z))
    return cells


def build_line_plane_cells(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    z: int,
) -> set[tuple[int, int, int]]:
    return {(x, y, z) for x, y in _rasterize_line(start_x, start_y, end_x, end_y)}


def build_shape_plane_cells(
    shape: str,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    z: int,
) -> set[tuple[int, int, int]]:
    normalized = shape.strip().lower()
    if normalized == "box":
        return build_box_plane_cells(start_x, start_y, end_x, end_y, z)
    if normalized == "line":
        return build_line_plane_cells(start_x, start_y, end_x, end_y, z)
    raise ValueError(f"Unsupported shape for plane cell generation: {shape}")


def _rasterize_line(start_x: int, start_y: int, end_x: int, end_y: int) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    x0, y0, x1, y1 = start_x, start_y, end_x, end_y
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx + dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return points
        error2 = 2 * error
        if error2 >= dy:
            error += dy
            x0 += sx
        if error2 <= dx:
            error += dx
            y0 += sy


def _plane_fill_bounds(voxels: VoxelGrid, z: int, seed_x: int, seed_y: int) -> tuple[int, int, int, int]:
    plane_cells = [(x, y) for x, y, cell_z, _ in voxels.to_list() if cell_z == z]
    if not plane_cells:
        return seed_x, seed_x, seed_y, seed_y
    xs = [cell[0] for cell in plane_cells] + [seed_x]
    ys = [cell[1] for cell in plane_cells] + [seed_y]
    return min(xs), max(xs), min(ys), max(ys)


def _expand_mirror_cells(ctx, base_cells: set[tuple[int, int, int]]) -> set[tuple[int, int, int]]:
    expand = getattr(ctx, "expand_mirrored_cells", None)
    if callable(expand):
        return expand(base_cells)
    return set(base_cells)


def _apply_voxel_mode(
    voxels: VoxelGrid,
    cells: set[tuple[int, int, int]],
    mode: str,
    color_index: int | None,
) -> list[_VoxelDelta]:
    if mode == "paint" and color_index is None:
        raise ValueError("Paint command requires color index.")

    deltas: list[_VoxelDelta] = []
    for x, y, z in sorted(cells):
        previous = voxels.get(x, y, z)
        deltas.append(_VoxelDelta(x=x, y=y, z=z, previous_color=previous))
        if mode == "erase":
            voxels.remove(x, y, z)
        else:
            voxels.set(x, y, z, color_index)  # type: ignore[arg-type]
    return deltas


def _invalidate_active_mesh_cache(ctx, cells: set[tuple[int, int, int]] | None = None) -> None:
    active_part = getattr(ctx, "active_part", None)
    if active_part is not None and hasattr(active_part, "mesh_cache"):
        if cells and hasattr(active_part, "mark_dirty_cells"):
            active_part.mark_dirty_cells(cells)
            return
        active_part.mesh_cache = None
        if hasattr(active_part, "dirty_bounds"):
            active_part.dirty_bounds = None


def _flood_plane_region(
    voxels: VoxelGrid,
    seed_x: int,
    seed_y: int,
    z: int,
    target_color: int | None,
    bounds: tuple[int, int, int, int],
    *,
    max_cells: int | None = None,
) -> set[tuple[int, int]] | None:
    min_x, max_x, min_y, max_y = bounds
    queue: list[tuple[int, int]] = [(seed_x, seed_y)]
    visited: set[tuple[int, int]] = set()
    connected: set[tuple[int, int]] = set()

    while queue:
        x, y = queue.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if x < min_x or x > max_x or y < min_y or y > max_y:
            continue
        if voxels.get(x, y, z) != target_color:
            continue
        connected.add((x, y))
        if max_cells is not None and len(connected) > max_cells:
            return None
        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))
    return connected


def _volume_fill_bounds(
    voxels: VoxelGrid,
    seed_x: int,
    seed_y: int,
    seed_z: int,
) -> tuple[int, int, int, int, int, int]:
    rows = voxels.to_list()
    if not rows:
        return seed_x, seed_x, seed_y, seed_y, seed_z, seed_z
    xs = [row[0] for row in rows] + [seed_x]
    ys = [row[1] for row in rows] + [seed_y]
    zs = [row[2] for row in rows] + [seed_z]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def _flood_volume_region(
    voxels: VoxelGrid,
    seed_x: int,
    seed_y: int,
    seed_z: int,
    target_color: int | None,
    bounds: tuple[int, int, int, int, int, int],
    *,
    max_cells: int | None = None,
) -> set[tuple[int, int, int]] | None:
    min_x, max_x, min_y, max_y, min_z, max_z = bounds
    queue: list[tuple[int, int, int]] = [(seed_x, seed_y, seed_z)]
    visited: set[tuple[int, int, int]] = set()
    connected: set[tuple[int, int, int]] = set()

    while queue:
        x, y, z = queue.pop()
        if (x, y, z) in visited:
            continue
        visited.add((x, y, z))
        if x < min_x or x > max_x or y < min_y or y > max_y or z < min_z or z > max_z:
            continue
        if voxels.get(x, y, z) != target_color:
            continue
        connected.add((x, y, z))
        if max_cells is not None and len(connected) > max_cells:
            return None
        queue.append((x + 1, y, z))
        queue.append((x - 1, y, z))
        queue.append((x, y + 1, z))
        queue.append((x, y - 1, z))
        queue.append((x, y, z + 1))
        queue.append((x, y, z - 1))
    return connected
