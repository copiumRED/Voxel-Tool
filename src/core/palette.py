from __future__ import annotations

DEFAULT_PALETTE: list[tuple[int, int, int]] = [
    (230, 80, 80),
    (240, 150, 70),
    (240, 220, 80),
    (110, 210, 110),
    (90, 170, 230),
    (140, 130, 230),
    (210, 110, 200),
    (220, 220, 220),
]


def normalize_palette(palette: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    if not palette:
        raise ValueError("Palette must contain at least one color.")
    normalized: list[tuple[int, int, int]] = []
    for entry in palette:
        if len(entry) != 3:
            raise ValueError("Each palette color must contain 3 channels (RGB).")
        r, g, b = entry
        channels = (int(r), int(g), int(b))
        if any(channel < 0 or channel > 255 for channel in channels):
            raise ValueError("Palette color channels must be in range 0..255.")
        normalized.append(channels)
    return normalized


def clamp_active_color_index(index: int, palette_size: int) -> int:
    if palette_size <= 0:
        raise ValueError("Palette size must be positive.")
    return max(0, min(index, palette_size - 1))
