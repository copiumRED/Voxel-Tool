from __future__ import annotations

from pathlib import Path

from core.io.project_io import load_project, save_project
from core.project import Project
from util.fs import get_app_temp_dir

_RECOVERY_FILE_NAME = "autosave_recovery.json"


def get_recovery_path() -> Path:
    return get_app_temp_dir("VoxelTool") / _RECOVERY_FILE_NAME


def has_recovery_snapshot() -> bool:
    return get_recovery_path().exists()


def save_recovery_snapshot(project: Project) -> Path:
    path = get_recovery_path()
    save_project(project, str(path))
    return path


def load_recovery_snapshot() -> Project:
    return load_project(str(get_recovery_path()))


def clear_recovery_snapshot() -> None:
    get_recovery_path().unlink(missing_ok=True)

