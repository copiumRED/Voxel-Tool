"""Core data models (Project/Part/Palette)."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class PaletteColor:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass
class Palette:
    colors: List[PaletteColor] = field(default_factory=list)


@dataclass
class Part:
    part_id: str
    name: str
    dims: Tuple[int, int, int] = (128, 128, 128)


@dataclass
class Project:
    project_id: str
    version: str = "0.1.0"
    parts: Dict[str, Part] = field(default_factory=dict)
    palette: Palette = field(default_factory=Palette)
