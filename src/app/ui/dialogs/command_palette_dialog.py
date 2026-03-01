from __future__ import annotations

from typing import Iterable

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class CommandPaletteDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.resize(460, 360)

        layout = QVBoxLayout(self)
        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText("Type to filter commands...")
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget(self)
        self.list_widget.itemDoubleClicked.connect(lambda _item: self.accept())
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._all_items: list[tuple[str, str]] = []

    def set_entries(self, entries: Iterable[tuple[str, str]]) -> None:
        self._all_items = [(str(command_id), str(label)) for command_id, label in entries]
        self._rebuild_list()

    def selected_command_id(self) -> str | None:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        value = item.data(0x0100)
        return value if isinstance(value, str) else None

    def _on_filter_changed(self, _text: str) -> None:
        self._rebuild_list()

    def _rebuild_list(self) -> None:
        query = self.filter_edit.text().strip().lower()
        self.list_widget.clear()
        for command_id, label in self._all_items:
            if query and query not in label.lower():
                continue
            item = QListWidgetItem(label)
            item.setData(0x0100, command_id)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
