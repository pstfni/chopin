"""Entrypoint to shuffle_playlist a playlist."""
import typer

from chopin.managers.playlist import shuffle_playlist
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def shuffle(
    name: str = typer.Argument(..., help="Name for your playlist"),
):
    """Shuffle an existing playlist."""
    typer.echo("🔀 Shuffling ...")
    playlist = shuffle_playlist(name)
    typer.echo(f"Playlist {playlist.name} successfully shuffled.")


def main():  # noqa: D103
    typer.run(shuffle_playlist)
