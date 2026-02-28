from __future__ import annotations

from core.commands.command import Command


class CommandStack:
    def __init__(self) -> None:
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []

    @property
    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def do(self, command: Command, ctx) -> None:
        command.do(ctx)
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self, ctx) -> None:
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.undo(ctx)
        self.redo_stack.append(command)

    def redo(self, ctx) -> None:
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        command.do(ctx)
        self.undo_stack.append(command)

    def clear(self) -> None:
        self.undo_stack.clear()
        self.redo_stack.clear()
