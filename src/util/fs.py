from __future__ import annotations

import os
import tempfile
from pathlib import Path


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def get_app_temp_dir(app_name: str) -> Path:
    safe_name = app_name.strip() or "App"
    repo_root = Path(__file__).resolve().parents[2]

    candidates: list[Path] = []
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / safe_name / "Temp")
    if os.environ.get("TEMP"):
        candidates.append(Path(os.environ["TEMP"]) / safe_name)
    if os.environ.get("TMP"):
        candidates.append(Path(os.environ["TMP"]) / safe_name)
    candidates.append(Path(tempfile.gettempdir()) / safe_name)
    candidates.append(Path.home() / "AppData" / "Local" / safe_name / "Temp")
    candidates.append(Path.home() / f".{safe_name}" / "Temp")

    for candidate in candidates:
        if _is_within(candidate, repo_root):
            continue
        if _is_writable_dir(candidate):
            return candidate

    raise RuntimeError("Could not create a writable temp directory outside the repository.")
