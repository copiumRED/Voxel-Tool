from __future__ import annotations

from app.app_context import AppContext
from core.commands.demo_commands import (
    BoxVoxelCommand,
    ClearVoxelsCommand,
    CreateTestVoxelsCommand,
    PaintVoxelCommand,
    RemoveVoxelCommand,
    RenameProjectCommand,
)
from core.project import Project


def test_rename_project_command_undo_redo() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))

    command = RenameProjectCommand("Demo")
    ctx.command_stack.do(command, ctx)
    assert ctx.current_project.name == "Demo"
    assert ctx.command_stack.can_undo is True
    assert ctx.command_stack.can_redo is False

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.name == "Untitled"
    assert ctx.command_stack.can_undo is False
    assert ctx.command_stack.can_redo is True

    ctx.command_stack.redo(ctx)
    assert ctx.current_project.name == "Demo"
    assert ctx.command_stack.can_undo is True
    assert ctx.command_stack.can_redo is False


def test_voxel_commands_undo_redo_counts() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))

    add_command = PaintVoxelCommand(1, 2, 3, 5)
    ctx.command_stack.do(add_command, ctx)
    assert ctx.current_project.voxels.count() == 1

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.count() == 0

    ctx.command_stack.redo(ctx)
    assert ctx.current_project.voxels.count() == 1

    ctx.command_stack.do(ClearVoxelsCommand(), ctx)
    assert ctx.current_project.voxels.count() == 0

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.count() == 1


def test_add_voxel_overwrite_undo_restores_previous_color() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.current_project.voxels.set(1, 2, 0, 3)

    ctx.command_stack.do(PaintVoxelCommand(1, 2, 0, 7), ctx)
    assert ctx.current_project.voxels.get(1, 2, 0) == 7

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.get(1, 2, 0) == 3


def test_remove_voxel_undo_restores_if_present() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.current_project.voxels.set(2, -1, 0, 5)

    ctx.command_stack.do(RemoveVoxelCommand(2, -1, 0), ctx)
    assert ctx.current_project.voxels.get(2, -1, 0) is None

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.get(2, -1, 0) == 5


def test_create_test_voxels_command_undo_redo_counts() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.current_project.voxels.set(9, 9, 9, 1)

    ctx.command_stack.do(CreateTestVoxelsCommand(center_color_index=2, arm_color_index=3), ctx)
    assert ctx.current_project.voxels.count() == 7
    assert ctx.current_project.voxels.get(0, 0, 0) == 2

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.count() == 1
    assert ctx.current_project.voxels.get(9, 9, 9) == 1

    ctx.command_stack.redo(ctx)
    assert ctx.current_project.voxels.count() == 7


def test_paint_and_erase_commands_overwrite_semantics() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    ctx.current_project.voxels.set(3, 3, 0, 1)

    ctx.command_stack.do(PaintVoxelCommand(3, 3, 0, 6), ctx)
    assert ctx.current_project.voxels.get(3, 3, 0) == 6

    ctx.command_stack.do(RemoveVoxelCommand(3, 3, 0), ctx)
    assert ctx.current_project.voxels.get(3, 3, 0) is None

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.get(3, 3, 0) == 6


def test_box_fill_and_erase_single_undo_per_operation() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))

    ctx.command_stack.do(BoxVoxelCommand(0, 0, 2, 1, z=0, mode="paint", color_index=4), ctx)
    assert ctx.current_project.voxels.count() == 6

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.count() == 0

    ctx.command_stack.redo(ctx)
    assert ctx.current_project.voxels.count() == 6

    ctx.command_stack.do(BoxVoxelCommand(1, 0, 2, 0, z=0, mode="erase"), ctx)
    assert ctx.current_project.voxels.count() == 4

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.voxels.count() == 6
