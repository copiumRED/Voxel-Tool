from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.analysis.stats import SceneStats


def format_runtime_stats_label(
    *,
    frame_ms: float,
    rebuild_ms: float,
    scene_triangles: int,
    scene_voxels: int,
    active_part_voxels: int,
) -> str:
    return (
        "Runtime: "
        f"frame {frame_ms:.2f} ms | rebuild {rebuild_ms:.2f} ms | "
        f"scene tris {scene_triangles} | scene voxels {scene_voxels} | "
        f"active-part voxels {active_part_voxels}"
    )


def format_memory_label(memory_bytes: int) -> str:
    value = float(max(0, int(memory_bytes)))
    units = ("B", "KB", "MB", "GB")
    unit_index = 0
    while value >= 1024.0 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    return f"{value:.2f} {units[unit_index]}"


class StatsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.scene_label = QLabel("Scene: tris 0 | faces 0 | edges 0 | verts 0 | materials 0")
        self.object_label = QLabel("Object: -")
        self.voxel_count_label = QLabel("Active Part Voxels: 0")
        self.runtime_label = QLabel(
            "Runtime: frame 0.00 ms | rebuild 0.00 ms | scene tris 0 | scene voxels 0 | active-part voxels 0"
        )
        layout.addWidget(self.scene_label)
        layout.addWidget(self.object_label)
        layout.addWidget(self.voxel_count_label)
        layout.addWidget(self.runtime_label)
        layout.addStretch(1)

    def set_scene_stats(self, scene_stats: SceneStats, active_part_id: str, active_voxel_count: int) -> None:
        self.scene_label.setText(
            "Scene: "
            f"tris {scene_stats.triangles} | faces {scene_stats.faces} | "
            f"edges {scene_stats.edges} | verts {scene_stats.vertices} | materials {scene_stats.materials_used} | "
            f"mem {format_memory_label(scene_stats.total_memory_bytes)}"
        )
        active_part = next((part for part in scene_stats.parts if part.part_id == active_part_id), None)
        if active_part is None:
            self.object_label.setText("Object: -")
        else:
            bx, by, bz = active_part.bounds_size
            mx, my, mz = active_part.bounds_meters
            self.object_label.setText(
                "Object: "
                f"{active_part.part_name} | tris {active_part.triangles} | faces {active_part.faces} | "
                f"edges {active_part.edges} | verts {active_part.vertices} | bounds {bx}x{by}x{bz} vox | "
                f"{mx:.2f}x{my:.2f}x{mz:.2f} m | "
                f"materials {active_part.materials_used} | "
                f"deg quads {active_part.degenerate_quads} | nm-edge hints {active_part.non_manifold_edge_hints} | "
                f"inc tries {active_part.incremental_rebuild_attempts} | "
                f"inc fallbacks {active_part.incremental_rebuild_fallbacks} | "
                f"vox mem {format_memory_label(active_part.voxel_memory_bytes)} | "
                f"mesh mem {format_memory_label(active_part.mesh_memory_bytes)}"
            )
        self.voxel_count_label.setText(f"Active Part Voxels: {active_voxel_count}")

    def set_runtime_stats(
        self,
        *,
        frame_ms: float,
        rebuild_ms: float,
        scene_triangles: int,
        scene_voxels: int,
        active_part_voxels: int,
    ) -> None:
        self.runtime_label.setText(
            format_runtime_stats_label(
                frame_ms=frame_ms,
                rebuild_ms=rebuild_ms,
                scene_triangles=scene_triangles,
                scene_voxels=scene_voxels,
                active_part_voxels=active_part_voxels,
            )
        )
