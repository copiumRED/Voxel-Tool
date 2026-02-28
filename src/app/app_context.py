from __future__ import annotations

from dataclasses import dataclass, field

from core.commands.command_stack import CommandStack
from core.palette import DEFAULT_PALETTE
from core.project import Project

@dataclass(slots=True)
class AppContext:
    current_project: Project
    current_path: str | None = None
    command_stack: CommandStack = field(default_factory=CommandStack)
    active_color_index: int = 0
    palette: list[tuple[int, int, int]] = field(default_factory=lambda: list(DEFAULT_PALETTE))

