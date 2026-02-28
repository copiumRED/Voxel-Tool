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
    second_part = project.scene.add_part("Part 2")
    project.scene.set_active_part(second_part.part_id)
    second_part.voxels.set(5, 0, -1, 6)
    second_part.visible = False
    second_part.locked = True
    path = get_app_temp_dir("VoxelTool") / f"test-project-{uuid.uuid4().hex}.json"
    try:
        save_project(project, str(path))
        loaded = load_project(str(path))
        assert loaded.name == project.name
        assert loaded.created_utc == project.created_utc
        assert loaded.modified_utc == project.modified_utc
        assert loaded.version == project.version
        assert len(loaded.scene.parts) == 2
        assert loaded.scene.active_part_id == second_part.part_id
        assert loaded.scene.parts[project.active_part_id].voxels.to_list() == second_part.voxels.to_list()
        assert loaded.scene.parts[project.active_part_id].visible is False
        assert loaded.scene.parts[project.active_part_id].locked is True
        first_part_id = next(part_id for part_id in loaded.scene.parts if part_id != second_part.part_id)
        assert loaded.scene.parts[first_part_id].voxels.get(1, 1, 1) == 3
        assert loaded.scene.parts[first_part_id].voxels.get(-2, 4, 0) == 7
        assert loaded.scene.parts[first_part_id].visible is True
        assert loaded.scene.parts[first_part_id].locked is False
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
    finally:
        path.unlink(missing_ok=True)
