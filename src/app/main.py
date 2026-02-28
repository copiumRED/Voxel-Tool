from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


def _ensure_src_on_path() -> None:
    src_dir = Path(__file__).resolve().parents[1]
    src_str = str(src_dir)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)


def main() -> int:
    _ensure_src_on_path()

    from app.app_context import AppContext
    from app.ui.main_window import MainWindow
    from util.log import get_logger

    logger = get_logger("voxel_tool")
    logger.info("Starting Phase-0 shell")

    app = QApplication(sys.argv)
    context = AppContext()
    window = MainWindow(context=context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

