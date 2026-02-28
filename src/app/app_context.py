from __future__ import annotations

from dataclasses import dataclass, field

from core.commands.command_stack import CommandStack
from core.palette import DEFAULT_PALETTE
from core.part import Part
from core.project import Project

@dataclass(slots=True)
class AppContext:
    current_project: Project
    current_path: str | None = None
    command_stack: CommandStack = field(default_factory=CommandStack)
    active_color_index: int = 0
    palette: list[tuple[int, int, int]] = field(default_factory=lambda: list(DEFAULT_PALETTE))

    @property
    def active_part(self) -> Part:
        return self.current_project.scene.get_active_part()

    @property
    def active_part_id(self) -> str:
        return self.active_part.part_id

    def set_active_part(self, part_id: str) -> None:
        self.current_project.scene.set_active_part(part_id)

