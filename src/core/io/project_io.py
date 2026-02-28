from __future__ import annotations

import json

from core.project import Project

_REQUIRED_KEYS = {"name", "created_utc", "modified_utc", "version"}


def save_project(project: Project, path: str) -> None:
    payload = {
        "name": project.name,
        "created_utc": project.created_utc,
        "modified_utc": project.modified_utc,
        "version": project.version,
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)


def load_project(path: str) -> Project:
    with open(path, "r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    keys = set(payload.keys())
    if keys != _REQUIRED_KEYS:
        missing = sorted(_REQUIRED_KEYS - keys)
        extra = sorted(keys - _REQUIRED_KEYS)
        details = []
        if missing:
            details.append(f"missing keys: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected keys: {', '.join(extra)}")
        raise ValueError(f"Invalid project schema ({'; '.join(details)}).")

    return Project(
        name=str(payload["name"]),
        created_utc=str(payload["created_utc"]),
        modified_utc=str(payload["modified_utc"]),
        version=int(payload["version"]),
    )
