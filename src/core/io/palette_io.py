from __future__ import annotations

import json
from pathlib import Path

from core.palette import normalize_palette


def _normalize_palette_metadata(metadata: dict[str, object] | None) -> dict[str, str]:
    source = metadata or {}
    return {
        "name": str(source.get("name", "")).strip(),
        "tags": str(source.get("tags", "")).strip(),
        "source": str(source.get("source", "")).strip(),
    }


def save_palette_preset(
    palette: list[tuple[int, int, int]],
    path: str,
    *,
    metadata: dict[str, object] | None = None,
) -> None:
    normalized = normalize_palette(palette)
    suffix = Path(path).suffix.lower()
    if suffix == ".gpl":
        _save_palette_gpl(normalized, path)
        return
    payload = {
        "palette": [[r, g, b] for r, g, b in normalized],
        "metadata": _normalize_palette_metadata(metadata),
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)


def load_palette_preset(path: str) -> list[tuple[int, int, int]]:
    palette, _metadata = load_palette_preset_with_metadata(path)
    return palette


def load_palette_preset_with_metadata(path: str) -> tuple[list[tuple[int, int, int]], dict[str, str]]:
    suffix = Path(path).suffix.lower()
    if suffix == ".gpl":
        return _load_palette_gpl(path), _normalize_palette_metadata(None)

    with open(path, "r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)
    if not isinstance(payload, dict):
        raise ValueError("Palette preset must be a JSON object.")
    raw_palette = payload.get("palette")
    if not isinstance(raw_palette, list):
        raise ValueError("Palette preset must include a 'palette' list.")
    converted: list[tuple[int, int, int]] = []
    for item in raw_palette:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError("Palette entries must be RGB triplets.")
        converted.append((int(item[0]), int(item[1]), int(item[2])))
    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("Palette metadata must be an object when present.")
    return normalize_palette(converted), _normalize_palette_metadata(metadata)


def _save_palette_gpl(palette: list[tuple[int, int, int]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("GIMP Palette\n")
        file_obj.write("Name: VoxelTool Palette\n")
        file_obj.write("Columns: 8\n")
        file_obj.write("#\n")
        for index, (r, g, b) in enumerate(palette, start=1):
            file_obj.write(f"{r:3d} {g:3d} {b:3d}\tColor {index}\n")


def _load_palette_gpl(path: str) -> list[tuple[int, int, int]]:
    rows: list[tuple[int, int, int]] = []
    with open(path, "r", encoding="utf-8") as file_obj:
        lines = file_obj.readlines()
    if not lines or not lines[0].strip().startswith("GIMP Palette"):
        raise ValueError("Invalid GPL palette header.")

    for raw_line in lines[1:]:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("name:") or line.lower().startswith("columns:"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            continue
        rows.append((r, g, b))
    if not rows:
        raise ValueError("GPL palette does not contain any colors.")
    return normalize_palette(rows)
