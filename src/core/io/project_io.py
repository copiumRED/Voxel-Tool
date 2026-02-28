from __future__ import annotations

import json

from core.project import Project
from core.voxels.voxel_grid import VoxelGrid

_REQUIRED_BASE_KEYS = {"name", "created_utc", "modified_utc", "version"}
_REQUIRED_KEYS = _REQUIRED_BASE_KEYS | {"voxels"}


def save_project(project: Project, path: str) -> None:
    payload = {
        "name": project.name,
        "created_utc": project.created_utc,
        "modified_utc": project.modified_utc,
        "version": project.version,
        "voxels": project.voxels.to_list(),
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)


def load_project(path: str) -> Project:
    with open(path, "r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    keys = set(payload.keys())
    missing = _REQUIRED_KEYS - keys
    extra = keys - _REQUIRED_KEYS
    if extra or (missing and missing != {"voxels"}):
        missing_sorted = sorted(missing)
        extra_sorted = sorted(extra)
        details = []
        if missing_sorted:
            details.append(f"missing keys: {', '.join(missing_sorted)}")
        if extra_sorted:
            details.append(f"unexpected keys: {', '.join(extra_sorted)}")
        raise ValueError(f"Invalid project schema ({'; '.join(details)}).")

    voxels = VoxelGrid.from_list(payload.get("voxels", []))

    project = Project(
        name=str(payload["name"]),
        created_utc=str(payload["created_utc"]),
        modified_utc=str(payload["modified_utc"]),
        version=int(payload["version"]),
    )
    project.voxels = voxels
    return project
