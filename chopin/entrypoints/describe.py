"""Describer entrypoint."""
from pathlib import Path

import typer

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.managers.track import TrackManager
from chopin.schemas.playlist import PlaylistSummary
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


def describe(
    output: Path = typer.Option(None, help="Output directory"),
    name: str = typer.Option(None, help="Specific name of a playlist to fetch. If none, all playlists are fetched"),
):
    """Retrieve data from a playlist and describe it.

    The playlist(s) (summarized as JSONs) will be written into files.
    """
    client = ClientManager(SpotifyClient().get_client())
    track_manager = TrackManager(client)
    playlist_manager = PlaylistManager(client)

    typer.echo("📝 Describing . . .")
    user_playlists = client.get_user_playlists()
    if name:
        target_playlists = [playlist for playlist in user_playlists if name == playlist.name]
    else:
        target_playlists = user_playlists

    for target_playlist in target_playlists:

        tracks = client.get_tracks(target_playlist.uri)
        tracks = track_manager.set_audio_features(tracks)
        summarized_playlist = PlaylistSummary(playlist=target_playlist, tracks=tracks)
        if output:
            out_file = output / f"{target_playlist.name}.json"
            typer.echo(f"Wrote playlist {target_playlist.name} in {out_file}")
            playlist_manager.dump(summarized_playlist, out_file)
        else:
            typer.echo(summarized_playlist)


def main():  # noqa: D103
    typer.run(describe)
