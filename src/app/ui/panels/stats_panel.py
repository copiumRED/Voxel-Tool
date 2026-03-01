from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.analysis.stats import SceneStats


class StatsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.scene_label = QLabel("Scene: tris 0 | faces 0 | edges 0 | verts 0 | materials 0")
        self.object_label = QLabel("Object: -")
        self.voxel_count_label = QLabel("Active Voxel Count: 0")
        self.runtime_label = QLabel("Runtime: frame 0.00 ms | rebuild 0.00 ms | scene tris 0 | active voxels 0")
        layout.addWidget(self.scene_label)
        layout.addWidget(self.object_label)
        layout.addWidget(self.voxel_count_label)
        layout.addWidget(self.runtime_label)
        layout.addStretch(1)

    def set_scene_stats(self, scene_stats: SceneStats, active_part_id: str, active_voxel_count: int) -> None:
        self.scene_label.setText(
            "Scene: "
            f"tris {scene_stats.triangles} | faces {scene_stats.faces} | "
            f"edges {scene_stats.edges} | verts {scene_stats.vertices} | materials {scene_stats.materials_used}"
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
                f"materials {active_part.materials_used}"
            )
        self.voxel_count_label.setText(f"Active Voxel Count: {active_voxel_count}")

    def set_runtime_stats(
        self,
        *,
        frame_ms: float,
        rebuild_ms: float,
        scene_triangles: int,
        active_voxels: int,
    ) -> None:
        self.runtime_label.setText(
            "Runtime: "
            f"frame {frame_ms:.2f} ms | rebuild {rebuild_ms:.2f} ms | "
            f"scene tris {scene_triangles} | active voxels {active_voxels}"
        )
