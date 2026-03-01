from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class VoxelGrid:
    _data: dict[tuple[int, int, int], int] = field(default_factory=dict)
    revision: int = 0

    def set(self, x: int, y: int, z: int, color_index: int) -> None:
        key = (x, y, z)
        color_value = int(color_index)
        if self._data.get(key) == color_value:
            return
        self._data[key] = color_value
        self.revision += 1

    def remove(self, x: int, y: int, z: int) -> None:
        key = (x, y, z)
        if key in self._data:
            del self._data[key]
            self.revision += 1

    def clear(self) -> None:
        if not self._data:
            return
        self._data.clear()
        self.revision += 1

    def get(self, x: int, y: int, z: int) -> int | None:
        return self._data.get((x, y, z))

    def count(self) -> int:
        return len(self._data)

    def to_list(self) -> list[list[int]]:
        rows: list[list[int]] = []
        for (x, y, z), color_index in sorted(self._data.items(), key=lambda item: item[0]):
            rows.append([x, y, z, color_index])
        return rows

    @classmethod
    def from_list(cls, data) -> "VoxelGrid":
        if not isinstance(data, list):
            raise ValueError("voxels must be a list.")

        grid = cls()
        for row in data:
            if not isinstance(row, (list, tuple)) or len(row) != 4:
                raise ValueError("each voxel row must have 4 integer values.")
            x, y, z, color_index = row
            if not all(isinstance(value, int) for value in (x, y, z, color_index)):
                raise ValueError("voxel row values must be integers.")
            grid.set(x, y, z, color_index)
        return grid
