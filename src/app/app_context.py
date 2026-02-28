from __future__ import annotations

from dataclasses import dataclass

from core.project import Project

@dataclass(slots=True)
class AppContext:
    current_project: Project
    current_path: str | None = None

