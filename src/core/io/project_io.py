from __future__ import annotations

import json

from core.part import Part
from core.project import Project
from core.scene import Scene
from core.voxels.voxel_grid import VoxelGrid

_REQUIRED_BASE_KEYS = {"name", "created_utc", "modified_utc", "version"}
_SCENE_KEY = "scene"
_LEGACY_VOXELS_KEY = "voxels"


def save_project(project: Project, path: str) -> None:
    parts_payload = []
    for part in project.scene.parts.values():
        parts_payload.append(
            {
                "part_id": part.part_id,
                "name": part.name,
                "voxels": part.voxels.to_list(),
                "visible": part.visible,
                "locked": part.locked,
            }
        )

    payload = {
        "name": project.name,
        "created_utc": project.created_utc,
        "modified_utc": project.modified_utc,
        "version": project.version,
        "scene": {
            "active_part_id": project.scene.active_part_id,
            "parts": parts_payload,
        },
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)


def load_project(path: str) -> Project:
    with open(path, "r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    if not isinstance(payload, dict):
        raise ValueError("Project file must contain a JSON object.")

    keys = set(payload.keys())
    if not _REQUIRED_BASE_KEYS.issubset(keys):
        missing = sorted(_REQUIRED_BASE_KEYS - keys)
        raise ValueError(f"Invalid project schema (missing keys: {', '.join(missing)}).")

    allowed = _REQUIRED_BASE_KEYS | {_SCENE_KEY, _LEGACY_VOXELS_KEY}
    extra = keys - allowed
    if extra:
        extra_sorted = sorted(extra)
        details = []
        if extra_sorted:
            details.append(f"unexpected keys: {', '.join(extra_sorted)}")
        raise ValueError(f"Invalid project schema ({'; '.join(details)}).")

    project = Project(
        name=str(payload["name"]),
        created_utc=str(payload["created_utc"]),
        modified_utc=str(payload["modified_utc"]),
        version=int(payload["version"]),
    )

    scene_payload = payload.get(_SCENE_KEY)
    if isinstance(scene_payload, dict):
        parts_payload = scene_payload.get("parts")
        if not isinstance(parts_payload, list):
            raise ValueError("Invalid project schema (scene.parts must be a list).")

        scene = Scene(parts={}, active_part_id=None)
        for raw_part in parts_payload:
            if not isinstance(raw_part, dict):
                raise ValueError("Invalid project schema (scene.parts items must be objects).")
            part_id = str(raw_part.get("part_id", "")).strip()
            name = str(raw_part.get("name", "")).strip()
            if not part_id or not name:
                raise ValueError("Invalid project schema (part_id and name are required for each part).")
            voxels = VoxelGrid.from_list(raw_part.get("voxels", []))
            visible = bool(raw_part.get("visible", True))
            locked = bool(raw_part.get("locked", False))
            scene.parts[part_id] = Part(
                part_id=part_id,
                name=name,
                voxels=voxels,
                visible=visible,
                locked=locked,
            )

        if not scene.parts:
            raise ValueError("Invalid project schema (scene must contain at least one part).")

        requested_active_part_id = str(scene_payload.get("active_part_id", "")).strip()
        if requested_active_part_id in scene.parts:
            scene.active_part_id = requested_active_part_id
        else:
            scene.active_part_id = next(iter(scene.parts.keys()))

        project.scene = scene
    else:
        project.voxels = VoxelGrid.from_list(payload.get(_LEGACY_VOXELS_KEY, []))

    return project
