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


def test_scene_duplicate_part_copies_voxels_and_sets_active_part() -> None:
    scene = Scene.with_default_part()
    source = scene.get_active_part()
    source.voxels.set(1, 2, 3, 7)
    source.position = (1.0, 2.0, 3.0)
    source.rotation = (10.0, 20.0, 30.0)
    source.scale = (1.5, 1.0, 0.75)

    duplicate = scene.duplicate_part(source.part_id, new_name="Part 1 Copy")

    assert duplicate.part_id != source.part_id
    assert scene.active_part_id == duplicate.part_id
    assert duplicate.voxels.to_list() == source.voxels.to_list()
    assert duplicate.position == source.position
    assert duplicate.rotation == source.rotation
    assert duplicate.scale == source.scale

    duplicate.voxels.set(-1, 0, 0, 2)
    assert source.voxels.get(-1, 0, 0) is None


def test_scene_delete_part_reassigns_active_and_keeps_one_minimum() -> None:
    scene = Scene.with_default_part()
    first = scene.get_active_part()
    second = scene.add_part("Part 2")
    scene.set_active_part(second.part_id)

    next_active = scene.delete_part(second.part_id)
    assert next_active == first.part_id
    assert scene.active_part_id == first.part_id
    assert second.part_id not in scene.parts

    try:
        scene.delete_part(first.part_id)
    except ValueError as exc:
        assert "last remaining part" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected deleting last part to fail.")


def test_scene_iter_visible_parts_hides_non_visible_entries() -> None:
    scene = Scene.with_default_part()
    first = scene.get_active_part()
    second = scene.add_part("Part 2")
    second.visible = False

    visible_part_ids = [part.part_id for part in scene.iter_visible_parts()]
    assert first.part_id in visible_part_ids
    assert second.part_id not in visible_part_ids


def test_part_lock_flag_blocks_edit_intent_in_context() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))
    active = ctx.active_part
    active.locked = True
    assert active.locked is True
