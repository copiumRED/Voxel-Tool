from __future__ import annotations

from app.app_context import AppContext
from core.commands.demo_commands import RenameProjectCommand
from core.project import Project


def test_rename_project_command_undo_redo() -> None:
    ctx = AppContext(current_project=Project(name="Untitled"))

    command = RenameProjectCommand("Demo")
    ctx.command_stack.do(command, ctx)
    assert ctx.current_project.name == "Demo"
    assert ctx.command_stack.can_undo is True
    assert ctx.command_stack.can_redo is False

    ctx.command_stack.undo(ctx)
    assert ctx.current_project.name == "Untitled"
    assert ctx.command_stack.can_undo is False
    assert ctx.command_stack.can_redo is True

    ctx.command_stack.redo(ctx)
    assert ctx.current_project.name == "Demo"
    assert ctx.command_stack.can_undo is True
    assert ctx.command_stack.can_redo is False
