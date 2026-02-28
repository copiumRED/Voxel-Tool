from __future__ import annotations

import json
import uuid

import pytest

from core.io.project_io import load_project, save_project
from core.project import Project
from util.fs import get_app_temp_dir


def test_project_save_load_roundtrip() -> None:
    project = Project(
        name="Demo",
        created_utc="2026-02-28T00:00:00+00:00",
        modified_utc="2026-02-28T00:05:00+00:00",
        version=1,
    )
    project.voxels.set(1, 1, 1, 3)
    project.voxels.set(-2, 4, 0, 7)
    project.editor_state = {
        "active_color_index": 3,
        "voxel_tool_mode": "erase",
        "mirror_x_enabled": True,
    }
    first_part_id = project.active_part_id
    second_part = project.scene.add_part("Part 2")
    third_part = project.scene.add_part("Part 3")
    project.scene.move_part(third_part.part_id, -1)
    project.scene.set_active_part(second_part.part_id)
    second_part.voxels.set(5, 0, -1, 6)
    second_part.position = (2.5, -1.0, 3.0)
    second_part.rotation = (0.0, 45.0, 0.0)
    second_part.scale = (1.0, 2.0, 1.0)
    second_part.visible = False
    second_part.locked = True
    group = project.scene.create_group("Group A")
    project.scene.assign_part_to_group(second_part.part_id, group.group_id)
    project.scene.set_group_locked(group.group_id, True)
    path = get_app_temp_dir("VoxelTool") / f"test-project-{uuid.uuid4().hex}.json"
    try:
        save_project(project, str(path))
        loaded = load_project(str(path))
        assert loaded.name == project.name
        assert loaded.created_utc == project.created_utc
        assert loaded.modified_utc == project.modified_utc
        assert loaded.version == project.version
        assert loaded.editor_state == project.editor_state
        assert len(loaded.scene.parts) == 3
        assert loaded.scene.active_part_id == second_part.part_id
        assert loaded.scene.parts[project.active_part_id].voxels.to_list() == second_part.voxels.to_list()
        assert loaded.scene.parts[project.active_part_id].position == (2.5, -1.0, 3.0)
        assert loaded.scene.parts[project.active_part_id].rotation == (0.0, 45.0, 0.0)
        assert loaded.scene.parts[project.active_part_id].scale == (1.0, 2.0, 1.0)
        assert loaded.scene.parts[project.active_part_id].visible is False
        assert loaded.scene.parts[project.active_part_id].locked is True
        assert loaded.scene.parts[first_part_id].voxels.get(1, 1, 1) == 3
        assert loaded.scene.parts[first_part_id].voxels.get(-2, 4, 0) == 7
        assert loaded.scene.parts[first_part_id].visible is True
        assert loaded.scene.parts[first_part_id].locked is False
        assert loaded.scene.part_order == project.scene.part_order
        assert len(loaded.scene.groups) == 1
        loaded_group = next(iter(loaded.scene.groups.values()))
        assert loaded_group.name == "Group A"
        assert second_part.part_id in loaded_group.part_ids
        assert loaded_group.locked is True
    finally:
        path.unlink(missing_ok=True)


def test_project_load_validates_required_keys() -> None:
    path = get_app_temp_dir("VoxelTool") / f"test-project-invalid-{uuid.uuid4().hex}.json"
    try:
        path.write_text(json.dumps({"name": "Demo"}), encoding="utf-8")
        with pytest.raises(ValueError):
            load_project(str(path))
    finally:
        path.unlink(missing_ok=True)


def test_project_load_older_schema_without_voxels() -> None:
    path = get_app_temp_dir("VoxelTool") / f"test-project-legacy-{uuid.uuid4().hex}.json"
    legacy_payload = {
        "name": "Legacy",
        "created_utc": "2026-02-28T00:00:00+00:00",
        "modified_utc": "2026-02-28T00:00:00+00:00",
        "version": 1,
    }
    try:
        path.write_text(json.dumps(legacy_payload), encoding="utf-8")
        loaded = load_project(str(path))
        assert loaded.name == "Legacy"
        assert loaded.voxels.count() == 0
        assert loaded.editor_state == {}
    finally:
        path.unlink(missing_ok=True)


def test_project_load_legacy_schema_with_root_voxels() -> None:
    path = get_app_temp_dir("VoxelTool") / f"test-project-legacy-voxels-{uuid.uuid4().hex}.json"
    legacy_payload = {
        "name": "Legacy Voxel Root",
        "created_utc": "2026-02-28T00:00:00+00:00",
        "modified_utc": "2026-02-28T00:00:00+00:00",
        "version": 1,
        "voxels": [[0, 0, 0, 2], [1, 0, 0, 3]],
    }
    try:
        path.write_text(json.dumps(legacy_payload), encoding="utf-8")
        loaded = load_project(str(path))
        assert loaded.voxels.count() == 2
        assert loaded.voxels.get(0, 0, 0) == 2
        assert loaded.voxels.get(1, 0, 0) == 3
        assert loaded.editor_state == {}
    finally:
        path.unlink(missing_ok=True)


def test_project_load_rejects_non_object_editor_state() -> None:
    path = get_app_temp_dir("VoxelTool") / f"test-project-editor-state-{uuid.uuid4().hex}.json"
    payload = {
        "name": "Bad EditorState",
        "created_utc": "2026-02-28T00:00:00+00:00",
        "modified_utc": "2026-02-28T00:00:00+00:00",
        "version": 1,
        "editor_state": [],
        "scene": {
            "active_part_id": "part-1",
            "parts": [{"part_id": "part-1", "name": "Part 1", "voxels": []}],
        },
    }
    try:
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError):
            load_project(str(path))
    finally:
        path.unlink(missing_ok=True)
