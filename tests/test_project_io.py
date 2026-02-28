from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.io.project_io import load_project, save_project
from core.project import Project


def test_project_save_load_roundtrip(tmp_path: Path) -> None:
    project = Project(
        name="Demo",
        created_utc="2026-02-28T00:00:00+00:00",
        modified_utc="2026-02-28T00:05:00+00:00",
        version=1,
    )
    path = tmp_path / "demo.json"

    save_project(project, str(path))
    loaded = load_project(str(path))

    assert loaded == project


def test_project_load_validates_required_keys(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps({"name": "Demo"}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_project(str(path))
