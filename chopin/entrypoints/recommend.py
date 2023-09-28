"""Entrypoint to create a recommended playlist."""
import typer

from chopin.constants import constants
from chopin.managers.playlist import create_playlist_from_recommendations


def recommend(
    name: str = typer.Argument(constants.RECOMMENDED_MIX.name, help="Name for your playlist"),
    nb_songs: int = typer.Argument(100, min=0, max=100, help="Number of songs for the playlist"),
):
    """Create a playlist from recommendations."""
    typer.echo("💡 Creating recommendations . . .")
    playlist = create_playlist_from_recommendations(name, nb_songs)
    typer.echo(f"Playlist {playlist.name} succesfully created")


def main():  # noqa: D103
    typer.run(recommend)
