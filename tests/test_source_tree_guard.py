from __future__ import annotations

from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "tests" / "fixtures" / "legacy_tree_manifest.txt"
LEGACY_ROOT = REPO_ROOT / "src" / "voxel_tool"


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _current_manifest_lines() -> list[str]:
    lines: list[str] = []
    for path in sorted(LEGACY_ROOT.rglob("*")):
        if (
            not path.is_file()
            or path.suffix != ".py"
            or "__pycache__" in path.parts
        ):
            continue
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        lines.append(f"{rel_path}|{_file_sha256(path)}")
    return lines


def test_legacy_source_tree_manifest_matches() -> None:
    expected_lines = [
        line.strip()
        for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    actual_lines = _current_manifest_lines()
    assert actual_lines == expected_lines, (
        "Legacy source tree changed under src/voxel_tool. "
        "Use src/app + src/core as canonical paths. "
        "If this change is intentional, regenerate tests/fixtures/legacy_tree_manifest.txt."
    )
