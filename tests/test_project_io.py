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
    path = get_app_temp_dir("VoxelTool") / f"test-project-{uuid.uuid4().hex}.json"
    try:
        save_project(project, str(path))
        loaded = load_project(str(path))
        assert loaded.name == project.name
        assert loaded.created_utc == project.created_utc
        assert loaded.modified_utc == project.modified_utc
        assert loaded.version == project.version
        assert loaded.voxels.to_list() == project.voxels.to_list()
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
