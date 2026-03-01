from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from core.part import Part
from core.voxels.voxel_grid import VoxelGrid

def _next_part_id() -> str:
    return f"part-{uuid4().hex}"


def _next_group_id() -> str:
    return f"group-{uuid4().hex}"


@dataclass(slots=True)
class PartGroup:
    group_id: str
    name: str
    part_ids: list[str] = field(default_factory=list)
    visible: bool = True
    locked: bool = False


@dataclass(slots=True)
class Scene:
    parts: dict[str, Part] = field(default_factory=dict)
    active_part_id: str | None = None
    part_order: list[str] = field(default_factory=list)
    groups: dict[str, PartGroup] = field(default_factory=dict)
    group_order: list[str] = field(default_factory=list)

    @classmethod
    def with_default_part(cls) -> "Scene":
        scene = cls()
        scene.add_part("Part 1")
        return scene

    def add_part(self, name: str) -> Part:
        part = Part(part_id=_next_part_id(), name=name)
        self.parts[part.part_id] = part
        self.part_order.append(part.part_id)
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

    def duplicate_part(self, part_id: str, *, new_name: str | None = None) -> Part:
        source = self.parts.get(part_id)
        if source is None:
            raise ValueError(f"Part '{part_id}' does not exist.")
        duplicate_name = new_name.strip() if new_name is not None else f"{source.name} Copy"
        if not duplicate_name:
            raise ValueError("Part name cannot be empty.")

        duplicated_voxels = VoxelGrid.from_list(source.voxels.to_list())
        duplicate = Part(
            part_id=_next_part_id(),
            name=duplicate_name,
            voxels=duplicated_voxels,
            position=source.position,
            rotation=source.rotation,
            scale=source.scale,
            visible=source.visible,
            locked=source.locked,
        )
        self.parts[duplicate.part_id] = duplicate
        self.part_order.append(duplicate.part_id)
        self.active_part_id = duplicate.part_id
        return duplicate

    def delete_part(self, part_id: str) -> str:
        if part_id not in self.parts:
            raise ValueError(f"Part '{part_id}' does not exist.")
        if len(self.parts) <= 1:
            raise ValueError("Cannot delete the last remaining part.")

        was_active = self.active_part_id == part_id
        del self.parts[part_id]
        self.part_order = [pid for pid in self.part_order if pid != part_id]
        for group in self.groups.values():
            group.part_ids = [pid for pid in group.part_ids if pid != part_id]
        if was_active:
            self.active_part_id = self.part_order[0]
        return self.active_part_id or ""

    def set_parts_visible(self, part_ids: list[str], visible: bool) -> list[str]:
        updated: list[str] = []
        for part_id in part_ids:
            part = self.parts.get(part_id)
            if part is None:
                continue
            part.visible = bool(visible)
            updated.append(part_id)
        return updated

    def set_parts_locked(self, part_ids: list[str], locked: bool) -> list[str]:
        updated: list[str] = []
        for part_id in part_ids:
            part = self.parts.get(part_id)
            if part is None:
                continue
            part.locked = bool(locked)
            updated.append(part_id)
        return updated

    def delete_parts(self, part_ids: list[str]) -> str:
        unique_ids = [part_id for part_id in dict.fromkeys(part_ids) if part_id in self.parts]
        if not unique_ids:
            raise ValueError("No valid parts selected for deletion.")
        if len(self.parts) - len(unique_ids) < 1:
            raise ValueError("Cannot delete all parts; at least one part must remain.")
        for part_id in unique_ids:
            self.delete_part(part_id)
        return self.active_part_id or ""

    def iter_visible_parts(self) -> list[Part]:
        return [part for _, part in self.iter_parts_ordered() if part.visible]

    def iter_parts_ordered(self) -> list[tuple[str, Part]]:
        if not self.part_order:
            self.part_order = list(self.parts.keys())
        return [(part_id, self.parts[part_id]) for part_id in self.part_order if part_id in self.parts]

    def move_part(self, part_id: str, direction: int) -> bool:
        if part_id not in self.parts or direction not in (-1, 1):
            return False
        if part_id not in self.part_order:
            self.part_order = list(self.parts.keys())
        index = self.part_order.index(part_id)
        target = index + direction
        if target < 0 or target >= len(self.part_order):
            return False
        self.part_order[index], self.part_order[target] = self.part_order[target], self.part_order[index]
        return True

    def create_group(self, name: str) -> PartGroup:
        group_name = name.strip()
        if not group_name:
            raise ValueError("Group name cannot be empty.")
        group = PartGroup(group_id=_next_group_id(), name=group_name)
        self.groups[group.group_id] = group
        self.group_order.append(group.group_id)
        return group

    def delete_group(self, group_id: str) -> None:
        if group_id not in self.groups:
            raise ValueError(f"Group '{group_id}' does not exist.")
        del self.groups[group_id]
        self.group_order = [gid for gid in self.group_order if gid != group_id]

    def assign_part_to_group(self, part_id: str, group_id: str) -> None:
        if part_id not in self.parts:
            raise ValueError(f"Part '{part_id}' does not exist.")
        group = self.groups.get(group_id)
        if group is None:
            raise ValueError(f"Group '{group_id}' does not exist.")
        if part_id not in group.part_ids:
            group.part_ids.append(part_id)

    def unassign_part_from_group(self, part_id: str, group_id: str) -> None:
        group = self.groups.get(group_id)
        if group is None:
            raise ValueError(f"Group '{group_id}' does not exist.")
        group.part_ids = [pid for pid in group.part_ids if pid != part_id]

    def set_group_visible(self, group_id: str, visible: bool) -> None:
        group = self.groups.get(group_id)
        if group is None:
            raise ValueError(f"Group '{group_id}' does not exist.")
        group.visible = bool(visible)
        for part_id in group.part_ids:
            part = self.parts.get(part_id)
            if part is not None:
                part.visible = group.visible

    def set_group_locked(self, group_id: str, locked: bool) -> None:
        group = self.groups.get(group_id)
        if group is None:
            raise ValueError(f"Group '{group_id}' does not exist.")
        group.locked = bool(locked)
        for part_id in group.part_ids:
            part = self.parts.get(part_id)
            if part is not None:
                part.locked = group.locked

    def group_names_for_part(self, part_id: str) -> list[str]:
        if part_id not in self.parts:
            raise ValueError(f"Part '{part_id}' does not exist.")
        names: list[str] = []
        for group_id, group in self.iter_groups_ordered():
            if part_id in group.part_ids:
                names.append(group.name or group_id)
        return names

    def iter_groups_ordered(self) -> list[tuple[str, PartGroup]]:
        if not self.group_order:
            self.group_order = list(self.groups.keys())
        return [(group_id, self.groups[group_id]) for group_id in self.group_order if group_id in self.groups]
