from __future__ import annotations

from dataclasses import dataclass, field

from core.commands.command_stack import CommandStack
from core.palette import DEFAULT_PALETTE
from core.part import Part
from core.project import Project

@dataclass(slots=True)
class AppContext:
    TOOL_MODE_PAINT = "paint"
    TOOL_MODE_ERASE = "erase"
    _VALID_TOOL_MODES = {TOOL_MODE_PAINT, TOOL_MODE_ERASE}

    current_project: Project
    current_path: str | None = None
    command_stack: CommandStack = field(default_factory=CommandStack)
    active_color_index: int = 0
    palette: list[tuple[int, int, int]] = field(default_factory=lambda: list(DEFAULT_PALETTE))
    voxel_tool_mode: str = TOOL_MODE_PAINT

    @property
    def active_part(self) -> Part:
        return self.current_project.scene.get_active_part()

    @property
    def active_part_id(self) -> str:
        return self.active_part.part_id

    def set_active_part(self, part_id: str) -> None:
        self.current_project.scene.set_active_part(part_id)

    def set_voxel_tool_mode(self, mode: str) -> None:
        if mode not in self._VALID_TOOL_MODES:
            raise ValueError(f"Unsupported voxel tool mode: {mode}")
        self.voxel_tool_mode = mode

