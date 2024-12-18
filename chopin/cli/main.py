"""Main and common entrypoint for the chopin cli."""

import typer

from chopin.cli.backup import backup
from chopin.cli.compose import compose
from chopin.cli.queue import queue
from chopin.cli.restore import restore
from chopin.cli.shuffle import shuffle

app = typer.Typer(rich_markup_mode="rich", pretty_exceptions_short=True)
app.add_typer(backup)
app.add_typer(compose)
app.add_typer(queue)
app.add_typer(restore)
app.add_typer(shuffle)
