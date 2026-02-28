from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AppContext:
    project_name: str = "Untitled"

