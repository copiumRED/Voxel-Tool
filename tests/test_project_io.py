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
    path = get_app_temp_dir("VoxelTool") / f"test-project-{uuid.uuid4().hex}.json"
    try:
        save_project(project, str(path))
        loaded = load_project(str(path))
        assert loaded == project
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
