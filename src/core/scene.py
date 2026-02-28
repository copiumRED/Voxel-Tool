from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

from core.part import Part

_PART_ID_COUNTER = count(start=1)


def _next_part_id() -> str:
    return f"part-{next(_PART_ID_COUNTER)}"


@dataclass(slots=True)
class Scene:
    parts: dict[str, Part] = field(default_factory=dict)
    active_part_id: str | None = None

    @classmethod
    def with_default_part(cls) -> "Scene":
        scene = cls()
        scene.add_part("Part 1")
        return scene

    def add_part(self, name: str) -> Part:
        part = Part(part_id=_next_part_id(), name=name)
        self.parts[part.part_id] = part
        if self.active_part_id is None:
            self.active_part_id = part.part_id
        return part

    def get_active_part(self) -> Part:
        if self.active_part_id is None:
            raise ValueError("Scene has no active part.")
        part = self.parts.get(self.active_part_id)
        if part is None:
            raise ValueError(f"Active part '{self.active_part_id}' does not exist.")
        return part

    def set_active_part(self, part_id: str) -> None:
        if part_id not in self.parts:
            raise ValueError(f"Part '{part_id}' does not exist.")
        self.active_part_id = part_id

    def rename_part(self, part_id: str, new_name: str) -> None:
        if part_id not in self.parts:
            raise ValueError(f"Part '{part_id}' does not exist.")
        name = new_name.strip()
        if not name:
            raise ValueError("Part name cannot be empty.")
        self.parts[part_id].name = name
