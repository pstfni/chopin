"""Create a playlist from the queue entrypoint."""

import click

from chopin.constants import constants
from chopin.managers.playlist import create_playlist_from_queue
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


@click.command()
@click.argument("name", type=str, default=constants.QUEUED_MIX.name, required=False)
def from_queue(name: str):
    """Create a playlist and shuffle it from the user's queue.

    !!! warning

        Due to Spotify API limits, you must be _playing_ a song on an
    active device for this to work.

    !!! warning

        Due to Spotify API limits, the maximum number of songs you can
    use is 20.
    """
    click.echo("🔮 Queuing . . .")
    create_playlist_from_queue(name)
    click.echo(f"Playlist '{name}' successfully created.")
