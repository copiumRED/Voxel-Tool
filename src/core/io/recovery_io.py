from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from core.io.project_io import load_project, save_project
from core.project import Project
from util.fs import get_app_temp_dir

_RECOVERY_FILE_NAME = "autosave_recovery.json"
_RECOVERY_EDITOR_STATE_KEY = "_recovery_version"
_RECOVERY_VERSION = 1


def get_recovery_path() -> Path:
    return get_app_temp_dir("VoxelTool") / _RECOVERY_FILE_NAME


def has_recovery_snapshot() -> bool:
    return get_recovery_path().exists()


def save_recovery_snapshot(project: Project) -> Path:
    path = get_recovery_path()
    snapshot = deepcopy(project)
    snapshot.editor_state = dict(project.editor_state)
    snapshot.editor_state[_RECOVERY_EDITOR_STATE_KEY] = _RECOVERY_VERSION
    save_project(snapshot, str(path))
    return path


def load_recovery_snapshot() -> Project:
    project = load_project(str(get_recovery_path()))
    raw_version = project.editor_state.get(_RECOVERY_EDITOR_STATE_KEY, _RECOVERY_VERSION)
    try:
        version = int(raw_version)
    except (TypeError, ValueError):
        raise ValueError("Invalid recovery snapshot version marker.")
    if version != _RECOVERY_VERSION:
        raise ValueError(f"Incompatible recovery snapshot version: {version}")
    project.editor_state.pop(_RECOVERY_EDITOR_STATE_KEY, None)
    return project


def clear_recovery_snapshot() -> None:
    get_recovery_path().unlink(missing_ok=True)

