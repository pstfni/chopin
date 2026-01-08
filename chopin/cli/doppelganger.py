"""Entrypoint to create a doppelganger: a similar playlist from an existing one."""

import click

from chopin.constants import constants
from chopin.managers.playlist import doppelganger_playlist
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


@click.command()
@click.argument("original_playlist", type=str)
@click.argument("new_playlist", type=str, default=constants.RECOMMENDED_MIX.name)
def doppelganger(original_playlist, new_playlist):
    """Create a doppelganger playlist from an existing one."""
    click.echo("👬 Creating doppelganger ...")
    playlist = doppelganger_playlist(original_playlist, new_playlist)
    click.echo(f"Playlist {playlist.name} successfully created.")
