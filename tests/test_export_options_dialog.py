from __future__ import annotations

from app.ui.main_window import _export_dialog_capabilities


def test_export_dialog_capabilities_obj_exposes_only_supported_controls() -> None:
    capabilities = _export_dialog_capabilities("OBJ")
    assert capabilities["obj_controls"] is True
    assert capabilities["scale_preset"] is True


def test_export_dialog_capabilities_gltf_exposes_scale_preset_only() -> None:
    capabilities = _export_dialog_capabilities("glTF")
    assert capabilities["obj_controls"] is False
    assert capabilities["scale_preset"] is True


def test_export_dialog_capabilities_vox_hides_unsupported_controls() -> None:
    capabilities = _export_dialog_capabilities("VOX")
    assert capabilities["obj_controls"] is False
    assert capabilities["scale_preset"] is False
