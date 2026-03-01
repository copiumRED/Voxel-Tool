from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt


@dataclass(slots=True)
class SurfaceMesh:
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    quads: list[tuple[int, int, int, int]] = field(default_factory=list)
    face_colors: list[int] = field(default_factory=list)

    @property
    def face_count(self) -> int:
        return len(self.quads)

    def quad_normal(self, index: int) -> tuple[float, float, float]:
        a, b, c, _ = self.quads[index]
        ax, ay, az = self.vertices[a]
        bx, by, bz = self.vertices[b]
        cx, cy, cz = self.vertices[c]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx = (uy * vz) - (uz * vy)
        ny = (uz * vx) - (ux * vz)
        nz = (ux * vy) - (uy * vx)
        length = sqrt((nx * nx) + (ny * ny) + (nz * nz))
        if length <= 1e-9:
            return (0.0, 0.0, 0.0)
        return (nx / length, ny / length, nz / length)
