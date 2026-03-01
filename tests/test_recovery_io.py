from __future__ import annotations

from core.io.recovery_io import (
    clear_recovery_snapshot,
    has_recovery_snapshot,
    load_recovery_snapshot,
    save_recovery_snapshot,
)
from core.project import Project


def test_recovery_snapshot_save_load_clear_cycle() -> None:
    clear_recovery_snapshot()
    project = Project(name="Recovery Test")
    project.voxels.set(1, 2, 3, 4)
    project.editor_state = {"voxel_tool_mode": "paint"}

    path = save_recovery_snapshot(project)
    assert path.exists()
    assert has_recovery_snapshot() is True

    loaded = load_recovery_snapshot()
    assert loaded.name == project.name
    assert loaded.voxels.get(1, 2, 3) == 4
    assert loaded.editor_state == project.editor_state

    clear_recovery_snapshot()
    assert has_recovery_snapshot() is False

