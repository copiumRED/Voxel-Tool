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
    def __init__(self, *, max_undo_steps: int = 200) -> None:
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self._transaction_commands: list[Command] | None = None
        self._transaction_label: str | None = None
        self.max_undo_steps = max(1, int(max_undo_steps))

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
            self._trim_undo_stack()
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

    def set_max_undo_steps(self, max_steps: int) -> None:
        self.max_undo_steps = max(1, int(max_steps))
        self._trim_undo_stack()

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
            self._trim_undo_stack()
            return
        self.undo_stack.append(_CompoundCommand(commands, label=label))
        self._trim_undo_stack()

    def _trim_undo_stack(self) -> None:
        overflow = len(self.undo_stack) - self.max_undo_steps
        if overflow > 0:
            del self.undo_stack[:overflow]
