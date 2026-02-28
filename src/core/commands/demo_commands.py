from __future__ import annotations

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


class AddVoxelCommand(Command):
    def __init__(self, x: int, y: int, z: int, color_index: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.color_index = color_index
        self._had_previous = False
        self._previous_color: int | None = None

    @property
    def name(self) -> str:
        return "Add Voxel"

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
        return "Remove Voxel"

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
