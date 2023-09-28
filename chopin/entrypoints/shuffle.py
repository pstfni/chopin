"""Entrypoint to shuffle a playlist."""
import typer

from chopin.client.playlists import get_named_playlist, get_playlist_tracks, replace_tracks_in_playlist
from chopin.managers.track import shuffle_tracks
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def shuffle(
    name: str = typer.Argument(..., help="Name for your playlist"),
):
    """Shuffle an existing playlist."""
    typer.echo("🔀 Shuffling ...")
    playlist = get_named_playlist(name)
    tracks = get_playlist_tracks(playlist.uri)
    tracks = shuffle_tracks(tracks)

    replace_tracks_in_playlist(playlist.uri, track_ids=[track.id for track in tracks])
    typer.echo(f"Playlist {playlist.name} successfully shuffled.")


def main():  # noqa: D103
    typer.run(shuffle)
