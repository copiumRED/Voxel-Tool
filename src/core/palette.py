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


def add_palette_color(
    palette: list[tuple[int, int, int]],
    color: tuple[int, int, int],
    *,
    index: int | None = None,
) -> list[tuple[int, int, int]]:
    next_palette = normalize_palette(list(palette))
    validated_color = normalize_palette([color])[0]
    if index is None:
        next_palette.append(validated_color)
    else:
        insert_at = max(0, min(int(index), len(next_palette)))
        next_palette.insert(insert_at, validated_color)
    return next_palette


def remove_palette_color(
    palette: list[tuple[int, int, int]],
    index: int,
) -> list[tuple[int, int, int]]:
    next_palette = normalize_palette(list(palette))
    if len(next_palette) <= 1:
        raise ValueError("Palette must contain at least one color.")
    remove_at = clamp_active_color_index(index, len(next_palette))
    del next_palette[remove_at]
    return next_palette


def swap_palette_colors(
    palette: list[tuple[int, int, int]],
    first_index: int,
    second_index: int,
) -> list[tuple[int, int, int]]:
    next_palette = normalize_palette(list(palette))
    i = clamp_active_color_index(first_index, len(next_palette))
    j = clamp_active_color_index(second_index, len(next_palette))
    next_palette[i], next_palette[j] = next_palette[j], next_palette[i]
    return next_palette
