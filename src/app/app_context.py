from __future__ import annotations

from dataclasses import dataclass, field

from core.commands.command_stack import CommandStack
from core.project import Project

@dataclass(slots=True)
class AppContext:
    current_project: Project
    current_path: str | None = None
    command_stack: CommandStack = field(default_factory=CommandStack)

