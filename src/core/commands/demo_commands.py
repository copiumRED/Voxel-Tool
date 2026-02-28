from __future__ import annotations

from dataclasses import dataclass

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
        self._had_previous = False
        self._previous_color: int | None = None

    @property
    def name(self) -> str:
        return "Paint Voxel"

    def do(self, ctx) -> None:
        previous = ctx.current_project.voxels.get(self.x, self.y, self.z)
        self._had_previous = previous is not None
        self._previous_color = previous
        ctx.current_project.voxels.set(self.x, self.y, self.z, self.color_index)

    def undo(self, ctx) -> None:
        if self._had_previous and self._previous_color is not None:
            ctx.current_project.voxels.set(self.x, self.y, self.z, self._previous_color)
            return
        ctx.current_project.voxels.remove(self.x, self.y, self.z)


class RemoveVoxelCommand(Command):
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self._had_previous = False
        self._previous_color: int | None = None

    @property
    def name(self) -> str:
        return "Erase Voxel"

    def do(self, ctx) -> None:
        previous = ctx.current_project.voxels.get(self.x, self.y, self.z)
        self._had_previous = previous is not None
        self._previous_color = previous
        ctx.current_project.voxels.remove(self.x, self.y, self.z)

    def undo(self, ctx) -> None:
        if self._had_previous and self._previous_color is not None:
            ctx.current_project.voxels.set(self.x, self.y, self.z, self._previous_color)


class ClearVoxelsCommand(Command):
    def __init__(self) -> None:
        self._snapshot: list[list[int]] = []

    @property
    def name(self) -> str:
        return "Clear Voxels"

    def do(self, ctx) -> None:
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
        self._deltas = []
        min_x, max_x = sorted((self.start_x, self.end_x))
        min_y, max_y = sorted((self.start_y, self.end_y))

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                previous = voxels.get(x, y, self.z)
                self._deltas.append(_VoxelDelta(x=x, y=y, z=self.z, previous_color=previous))
                if self.mode == "erase":
                    voxels.remove(x, y, self.z)
                else:
                    if self.color_index is None:
                        raise ValueError("Box paint command requires a color index.")
                    voxels.set(x, y, self.z, self.color_index)

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
        self._deltas = []
        for x, y in _rasterize_line(self.start_x, self.start_y, self.end_x, self.end_y):
            previous = voxels.get(x, y, self.z)
            self._deltas.append(_VoxelDelta(x=x, y=y, z=self.z, previous_color=previous))
            if self.mode == "erase":
                voxels.remove(x, y, self.z)
            else:
                if self.color_index is None:
                    raise ValueError("Line paint command requires a color index.")
                voxels.set(x, y, self.z, self.color_index)

    def undo(self, ctx) -> None:
        voxels = ctx.current_project.voxels
        for delta in self._deltas:
            if delta.previous_color is None:
                voxels.remove(delta.x, delta.y, delta.z)
            else:
                voxels.set(delta.x, delta.y, delta.z, delta.previous_color)


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
