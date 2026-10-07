"""Bare ``jarvis`` opens the one-key graphical setup."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import click


def check_and_route(ctx: click.Context) -> None:
    """Leave explicit subcommands alone; open the daily-use app otherwise."""
    if ctx.invoked_subcommand is not None:
        return
    from openjarvis.cli.gui_cmd import gui

    ctx.invoke(gui)
