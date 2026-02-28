from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from util.fs import get_app_temp_dir

_LOG_NAME = "voxel_tool.log"


def get_logger(name: str = "voxel_tool") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_dir = get_app_temp_dir("VoxelTool")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / _LOG_NAME

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=512_000,
        backupCount=2,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger

