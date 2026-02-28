from __future__ import annotations

import json

from core.palette import normalize_palette


def save_palette_preset(palette: list[tuple[int, int, int]], path: str) -> None:
    normalized = normalize_palette(palette)
    payload = {"palette": [[r, g, b] for r, g, b in normalized]}
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)


def load_palette_preset(path: str) -> list[tuple[int, int, int]]:
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
    return normalize_palette(converted)
