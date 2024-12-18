"""Entrypoint to shuffle_playlist a playlist."""

import click

from chopin.managers.playlist import shuffle_playlist
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


@click.command()
@click.argument("name", type=str)
def shuffle(
    name: str,
):
    """Shuffle an existing playlist."""
    click.echo("🔀 Shuffling ...")
    playlist = shuffle_playlist(name)
    click.echo(f"Playlist {playlist.name} successfully shuffled.")
