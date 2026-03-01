from __future__ import annotations

from pathlib import Path


def test_packaging_script_emits_diagnostic_artifact_lines() -> None:
    content = Path("tools/package_windows.ps1").read_text(encoding="utf-8")
    assert "ARTIFACT_EXE=" in content
    assert "ARTIFACT_SIZE_BYTES=" in content
    assert "ARTIFACT_SHA256=" in content
    assert "[PASS] Packaging complete." in content


def test_packaging_script_checks_packaged_executable_exists() -> None:
    content = Path("tools/package_windows.ps1").read_text(encoding="utf-8")
    assert "Assert-PathExists -PathValue $exePath -Label \"Packaged executable\"" in content
