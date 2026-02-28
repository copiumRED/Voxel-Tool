from __future__ import annotations

from core.commands.command import Command


class _CompoundCommand(Command):
    def __init__(self, commands: list[Command], label: str | None = None) -> None:
        self._commands = list(commands)
        self._label = label or "Transaction"

    @property
    def name(self) -> str:
        return self._label

    def do(self, ctx) -> None:
        for command in self._commands:
            command.do(ctx)

    def undo(self, ctx) -> None:
        for command in reversed(self._commands):
            command.undo(ctx)


class CommandStack:
    def __init__(self) -> None:
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self._transaction_commands: list[Command] | None = None
        self._transaction_label: str | None = None

    @property
    def can_undo(self) -> bool:
        return bool(self.undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self.redo_stack)

    def do(self, command: Command, ctx) -> None:
        command.do(ctx)
        if self._transaction_commands is not None:
            self._transaction_commands.append(command)
        else:
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

    def begin_transaction(self, label: str = "Transaction") -> None:
        if self._transaction_commands is not None:
            raise RuntimeError("A transaction is already active.")
        self._transaction_commands = []
        self._transaction_label = label

    def end_transaction(self) -> None:
        if self._transaction_commands is None:
            raise RuntimeError("No active transaction to end.")
        commands = self._transaction_commands
        label = self._transaction_label
        self._transaction_commands = None
        self._transaction_label = None

        if not commands:
            return
        if len(commands) == 1:
            self.undo_stack.append(commands[0])
            return
        self.undo_stack.append(_CompoundCommand(commands, label=label))
