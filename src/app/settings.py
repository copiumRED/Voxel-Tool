from __future__ import annotations

from PySide6.QtCore import QSettings


def get_settings() -> QSettings:
    return QSettings("CopiumRED", "VoxelTool")
