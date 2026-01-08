"""Main and common entrypoint for the chopin cli."""

import click

from chopin.cli.app import app as webapp
from chopin.cli.backup import backup
from chopin.cli.compose import compose
from chopin.cli.doppelganger import doppelganger
from chopin.cli.from_queue import from_queue
from chopin.cli.restore import restore
from chopin.cli.shuffle import shuffle


@click.group(name="chopin")
def app():
    """Manage and compose playlists.

    [bold red] ah [/bold red] [dim]
    """
    pass


app.add_command(backup)
app.add_command(compose)
app.add_command(from_queue)
app.add_command(restore)
app.add_command(shuffle)
app.add_command(webapp)
app.add_command(doppelganger)

if __name__ == "__main__":
    app()
