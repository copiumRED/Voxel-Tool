from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatsPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.voxel_count_label = QLabel("Voxel Count: 0")
        layout.addWidget(self.voxel_count_label)
        layout.addStretch(1)

    def set_voxel_count(self, count: int) -> None:
        self.voxel_count_label.setText(f"Voxel Count: {count}")
