from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SurfaceMesh:
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    quads: list[tuple[int, int, int, int]] = field(default_factory=list)
    face_colors: list[int] = field(default_factory=list)

    @property
    def face_count(self) -> int:
        return len(self.quads)
