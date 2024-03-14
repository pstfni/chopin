"""Create a playlist from the queue entrypoint."""

import typer

from chopin.constants import constants
from chopin.managers.playlist import create_playlist_from_queue
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def queue(
    name: str = typer.Argument(constants.QUEUED_MIX.name, help="Name for your playlist"),
):
    """Create a playlist and shuffle_playlist it from the user's queue.

    !!! warning     Due to Spotify API limits, you must be _playing_ a
    song on an active device for this to work.

    !!! warning     Due to Spotify API limits, the maximum number of
    songs you can use is 20.
    """
    typer.echo("🔮 Queuing . . .")
    create_playlist_from_queue(name)
    typer.echo(f"Playlist '{name}' successfully created.")


def main():  # noqa: D103
    typer.run(queue)
