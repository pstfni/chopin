"""Entrypoint to shuffle a playlist."""
import typer

from chopin.managers.client import ClientManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.managers.track import shuffle_tracks
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def shuffle(
    name: str = typer.Argument(..., help="Name for your playlist"),
):
    """Shuffle an existing playlist."""
    client = ClientManager(SpotifyClient().get_client())

    typer.echo("🔀 Shuffling ...")
    playlist = client.get_named_playlist(name)
    tracks = client.get_tracks(playlist.uri)
    tracks = shuffle_tracks(tracks)

    client.replace_tracks_in_playlist(playlist.uri, track_ids=[track.id for track in tracks])
    typer.echo(f"Playlist {playlist.name} successfully shuffled.")


def main():  # noqa: D103
    typer.run(shuffle)
