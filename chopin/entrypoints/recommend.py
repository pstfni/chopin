"""Entrypoint to create a recommended playlist."""

from typing import Annotated

import typer

from chopin.constants import constants
from chopin.managers.playlist import create_playlist_from_recommendations


def recommend(
    name: Annotated[str, typer.Argument(..., help="Name for your playlist")] = constants.RECOMMENDED_MIX.name,
    nb_songs: Annotated[int, typer.Argument(..., min=0, max=100, help="Number of songs for the playlist")] = 100,
):
    """Create a playlist from recommendations."""
    typer.echo("💡 Creating recommendations . . .")
    playlist = create_playlist_from_recommendations(name, nb_songs)
    typer.echo(f"Playlist {playlist.name} succesfully created")


def main():  # noqa: D103
    typer.run(recommend)
