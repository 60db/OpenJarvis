"""Bare Jarvis opens the graphical key-and-voice setup."""

from unittest.mock import MagicMock

from openjarvis.cli._first_run import check_and_route
from openjarvis.cli.gui_cmd import gui


def test_bare_jarvis_opens_setup():
    ctx = MagicMock(invoked_subcommand=None)
    check_and_route(ctx)
    ctx.invoke.assert_called_once_with(gui)


def test_explicit_subcommand_is_unchanged():
    ctx = MagicMock(invoked_subcommand="ask")
    check_and_route(ctx)
    ctx.invoke.assert_not_called()
