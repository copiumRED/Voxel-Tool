from __future__ import annotations

from app.app_context import AppContext
from core.commands.demo_commands import PaintVoxelCommand
from core.project import Project
from core.scene import Scene


def test_new_project_has_default_scene_with_active_part() -> None:
    project = Project(name="Untitled")
    assert len(project.scene.parts) == 1
    active_part = project.scene.get_active_part()
    assert active_part.name == "Part 1"
    assert project.active_part_id == active_part.part_id


def test_active_part_switch_changes_voxel_authority_for_commands() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    first_part = ctx.active_part
    second_part = ctx.current_project.scene.add_part("Part 2")

    ctx.command_stack.do(PaintVoxelCommand(1, 2, 3, 4), ctx)
    assert first_part.voxels.count() == 1
    assert second_part.voxels.count() == 0

    ctx.set_active_part(second_part.part_id)
    ctx.command_stack.do(PaintVoxelCommand(-1, 0, 5, 2), ctx)
    assert first_part.voxels.count() == 1
    assert second_part.voxels.count() == 1
    assert ctx.current_project.voxels.get(-1, 0, 5) == 2


def test_scene_add_rename_and_select_active_part() -> None:
    scene = Scene.with_default_part()
    first_active_id = scene.active_part_id
    assert first_active_id is not None

    second = scene.add_part("Blockout")
    scene.rename_part(second.part_id, "Blockout B")
    scene.set_active_part(second.part_id)

    assert scene.active_part_id == second.part_id
    assert scene.parts[second.part_id].name == "Blockout B"
    assert first_active_id in scene.parts
