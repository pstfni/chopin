"""Entrypoint to create a recommended playlist."""
import typer

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient


def recommend(
    name: str = typer.Argument("💡 Recommended Mix", help="Name for your playlist"),
    nb_songs: int = typer.Argument(100, min=0, max=100, help="Number of songs for the playlist"),
):
    """Create a playlist from recommendations."""
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)
    typer.echo("💡 Creating recommendations . . .")
    playlist = playlist_manager.create_playlist_from_recommendations(name, nb_songs)
    typer.echo(f"Playlist {playlist.name} succesfully created")


def main():  # noqa: D103
    typer.run(recommend)
