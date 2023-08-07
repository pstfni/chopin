"""Entrypoint to shuffle a playlist."""
import typer

from chopin.managers.client import ClientManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.managers.track import shuffle_tracks
from chopin.tools.logger import get_logger
from chopin.tools.strings import simplify_string

LOGGER = get_logger(__name__)


def shuffle(
    name: str = typer.Argument(..., help="Name for your playlist"),
):
    """Shuffle an existing playlist."""
    client = ClientManager(SpotifyClient().get_client())

    target_playlists = [playlist for playlist in client.get_user_playlists() if simplify_string(name) == playlist.name]

    if not target_playlists:
        raise ValueError(f"Playlist {name} not found in user playlists")

    typer.echo("🔀 Shuffling ...")
    playlist = target_playlists[0]
    tracks = client.get_tracks(playlist.uri)
    tracks = shuffle_tracks(tracks)

    client.replace_tracks_in_playlist(playlist.uri, track_ids=[track.id for track in tracks])
    typer.echo(f"Playlist {playlist.name} successfully shuffled.")


def main():  # noqa: D103
    typer.run(shuffle)
