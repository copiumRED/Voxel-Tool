from __future__ import annotations

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from util.fs import get_app_temp_dir

SAFE_TEMP_DIR = get_app_temp_dir("VoxelTool")
os.environ["TMP"] = str(SAFE_TEMP_DIR)
os.environ["TEMP"] = str(SAFE_TEMP_DIR)
os.environ["TMPDIR"] = str(SAFE_TEMP_DIR)
