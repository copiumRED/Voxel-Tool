from __future__ import annotations

from app.app_context import AppContext
from core.commands.demo_commands import BoxVoxelCommand, FillVoxelCommand, PaintVoxelCommand
from core.project import Project


def test_expand_mirrored_cells_xyz() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.set_mirror_axis("x", True)
    ctx.set_mirror_axis("y", True)
    ctx.set_mirror_axis("z", True)

    expanded = ctx.expand_mirrored_cells({(2, 1, -3)})
    assert expanded == {
        (2, 1, -3),
        (-2, 1, -3),
        (2, -1, -3),
        (-2, -1, -3),
        (2, 1, 3),
        (-2, 1, 3),
        (2, -1, 3),
        (-2, -1, 3),
    }


def test_paint_and_box_apply_mirror_x() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.set_mirror_axis("x", True)

    ctx.command_stack.do(PaintVoxelCommand(1, 0, 0, 4), ctx)
    assert ctx.current_project.voxels.get(1, 0, 0) == 4
    assert ctx.current_project.voxels.get(-1, 0, 0) == 4

    ctx.command_stack.do(BoxVoxelCommand(0, 0, 1, 0, z=0, mode="paint", color_index=3), ctx)
    assert ctx.current_project.voxels.get(1, 0, 0) == 3
    assert ctx.current_project.voxels.get(-1, 0, 0) == 3


def test_fill_applies_mirror_y() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.set_mirror_axis("y", True)
    voxels = ctx.current_project.voxels
    voxels.set(1, 1, 0, 2)
    voxels.set(2, 1, 0, 2)
    voxels.set(1, -1, 0, 2)
    voxels.set(2, -1, 0, 2)

    ctx.command_stack.do(FillVoxelCommand(1, 1, 0, mode="paint", color_index=6), ctx)
    assert voxels.get(1, 1, 0) == 6
    assert voxels.get(2, 1, 0) == 6
    assert voxels.get(1, -1, 0) == 6
    assert voxels.get(2, -1, 0) == 6
