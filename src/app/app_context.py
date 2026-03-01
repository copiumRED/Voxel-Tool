from __future__ import annotations

from dataclasses import dataclass, field

from core.commands.command_stack import CommandStack
from core.palette import DEFAULT_PALETTE
from core.part import Part
from core.project import Project

@dataclass(slots=True)
class AppContext:
    TOOL_MODE_PAINT = "paint"
    TOOL_MODE_ERASE = "erase"
    TOOL_SHAPE_BRUSH = "brush"
    TOOL_SHAPE_BOX = "box"
    TOOL_SHAPE_LINE = "line"
    TOOL_SHAPE_FILL = "fill"
    PICK_MODE_SURFACE = "surface"
    PICK_MODE_PLANE_LOCK = "plane_lock"
    EDIT_PLANE_XY = "xy"
    EDIT_PLANE_YZ = "yz"
    EDIT_PLANE_XZ = "xz"
    FILL_CONNECTIVITY_PLANE = "plane"
    FILL_CONNECTIVITY_VOLUME = "volume"
    CAMERA_PROJECTION_PERSPECTIVE = "perspective"
    CAMERA_PROJECTION_ORTHOGRAPHIC = "orthographic"
    NAV_PROFILE_CLASSIC = "classic"
    NAV_PROFILE_MMB_ORBIT = "mmb_orbit"
    NAV_PROFILE_BLENDER_MIX = "blender_mix"
    _VALID_TOOL_MODES = {TOOL_MODE_PAINT, TOOL_MODE_ERASE}
    _VALID_TOOL_SHAPES = {TOOL_SHAPE_BRUSH, TOOL_SHAPE_BOX, TOOL_SHAPE_LINE, TOOL_SHAPE_FILL}

    current_project: Project
    current_path: str | None = None
    command_stack: CommandStack = field(default_factory=CommandStack)
    active_color_index: int = 0
    palette: list[tuple[int, int, int]] = field(default_factory=lambda: list(DEFAULT_PALETTE))
    voxel_tool_mode: str = TOOL_MODE_PAINT
    voxel_tool_shape: str = TOOL_SHAPE_BRUSH
    brush_size: int = 1
    brush_shape: str = "cube"
    pick_mode: str = PICK_MODE_PLANE_LOCK
    edit_plane: str = EDIT_PLANE_XY
    grid_visible: bool = True
    grid_spacing: int = 1
    camera_snap_enabled: bool = False
    camera_snap_degrees: int = 15
    camera_projection: str = CAMERA_PROJECTION_PERSPECTIVE
    navigation_profile: str = NAV_PROFILE_CLASSIC
    mirror_x_enabled: bool = False
    mirror_y_enabled: bool = False
    mirror_z_enabled: bool = False
    mirror_x_offset: int = 0
    mirror_y_offset: int = 0
    mirror_z_offset: int = 0
    fill_max_cells: int = 5000
    fill_connectivity: str = FILL_CONNECTIVITY_PLANE
    locked_palette_slots: set[int] = field(default_factory=set)
    _VALID_BRUSH_SHAPES = {"cube", "sphere"}
    _VALID_PICK_MODES = {PICK_MODE_SURFACE, PICK_MODE_PLANE_LOCK}
    _VALID_EDIT_PLANES = {EDIT_PLANE_XY, EDIT_PLANE_YZ, EDIT_PLANE_XZ}
    _VALID_FILL_CONNECTIVITY = {FILL_CONNECTIVITY_PLANE, FILL_CONNECTIVITY_VOLUME}
    _VALID_CAMERA_PROJECTIONS = {CAMERA_PROJECTION_PERSPECTIVE, CAMERA_PROJECTION_ORTHOGRAPHIC}
    _VALID_NAVIGATION_PROFILES = {NAV_PROFILE_CLASSIC, NAV_PROFILE_MMB_ORBIT, NAV_PROFILE_BLENDER_MIX}

    @property
    def active_part(self) -> Part:
        return self.current_project.scene.get_active_part()

    @property
    def active_part_id(self) -> str:
        return self.active_part.part_id

    def set_active_part(self, part_id: str) -> None:
        self.current_project.scene.set_active_part(part_id)

    def set_voxel_tool_mode(self, mode: str) -> None:
        if mode not in self._VALID_TOOL_MODES:
            raise ValueError(f"Unsupported voxel tool mode: {mode}")
        self.voxel_tool_mode = mode

    def set_voxel_tool_shape(self, shape: str) -> None:
        if shape not in self._VALID_TOOL_SHAPES:
            raise ValueError(f"Unsupported voxel tool shape: {shape}")
        self.voxel_tool_shape = shape

    def set_brush_size(self, size: int) -> None:
        size_value = int(size)
        if size_value < 1 or size_value > 3:
            raise ValueError(f"Unsupported brush size: {size_value}")
        self.brush_size = size_value

    def set_brush_shape(self, shape: str) -> None:
        shape_value = str(shape).strip().lower()
        if shape_value not in self._VALID_BRUSH_SHAPES:
            raise ValueError(f"Unsupported brush shape: {shape_value}")
        self.brush_shape = shape_value

    def set_pick_mode(self, mode: str) -> None:
        mode_value = str(mode).strip().lower()
        if mode_value not in self._VALID_PICK_MODES:
            raise ValueError(f"Unsupported pick mode: {mode_value}")
        self.pick_mode = mode_value

    def set_edit_plane(self, plane: str) -> None:
        plane_value = str(plane).strip().lower()
        if plane_value not in self._VALID_EDIT_PLANES:
            raise ValueError(f"Unsupported edit plane: {plane_value}")
        self.edit_plane = plane_value

    def set_camera_projection(self, projection: str) -> None:
        projection_value = str(projection).strip().lower()
        if projection_value not in self._VALID_CAMERA_PROJECTIONS:
            raise ValueError(f"Unsupported camera projection: {projection_value}")
        self.camera_projection = projection_value

    def set_navigation_profile(self, profile: str) -> None:
        profile_value = str(profile).strip().lower()
        if profile_value not in self._VALID_NAVIGATION_PROFILES:
            raise ValueError(f"Unsupported navigation profile: {profile_value}")
        self.navigation_profile = profile_value

    def set_fill_connectivity(self, mode: str) -> None:
        mode_value = str(mode).strip().lower()
        if mode_value not in self._VALID_FILL_CONNECTIVITY:
            raise ValueError(f"Unsupported fill connectivity: {mode_value}")
        self.fill_connectivity = mode_value

    def set_palette_slot_locked(self, index: int, locked: bool) -> None:
        slot = int(index)
        if slot < 0:
            raise ValueError(f"Invalid palette slot index: {slot}")
        if locked:
            self.locked_palette_slots.add(slot)
            return
        self.locked_palette_slots.discard(slot)

    def is_palette_slot_locked(self, index: int) -> bool:
        return int(index) in self.locked_palette_slots

    def set_mirror_axis(self, axis: str, enabled: bool) -> None:
        if axis == "x":
            self.mirror_x_enabled = enabled
            return
        if axis == "y":
            self.mirror_y_enabled = enabled
            return
        if axis == "z":
            self.mirror_z_enabled = enabled
            return
        raise ValueError(f"Unsupported mirror axis: {axis}")

    def set_mirror_offset(self, axis: str, offset: int) -> None:
        if axis == "x":
            self.mirror_x_offset = int(offset)
            return
        if axis == "y":
            self.mirror_y_offset = int(offset)
            return
        if axis == "z":
            self.mirror_z_offset = int(offset)
            return
        raise ValueError(f"Unsupported mirror axis: {axis}")

    def expand_mirrored_cells(self, cells: set[tuple[int, int, int]]) -> set[tuple[int, int, int]]:
        expanded: set[tuple[int, int, int]] = set()
        for x, y, z in cells:
            mirror_x = (2 * self.mirror_x_offset) - x
            mirror_y = (2 * self.mirror_y_offset) - y
            mirror_z = (2 * self.mirror_z_offset) - z
            xs = (x, mirror_x) if self.mirror_x_enabled else (x,)
            ys = (y, mirror_y) if self.mirror_y_enabled else (y,)
            zs = (z, mirror_z) if self.mirror_z_enabled else (z,)
            for mirrored_x in xs:
                for mirrored_y in ys:
                    for mirrored_z in zs:
                        expanded.add((mirrored_x, mirrored_y, mirrored_z))
        return expanded

