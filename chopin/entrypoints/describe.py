"""Describer entrypoint."""

from pathlib import Path

import typer

from chopin.client.playlists import get_named_playlist, get_playlist_tracks, get_user_playlists
from chopin.managers.playlist import dump
from chopin.managers.track import set_audio_features
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
    typer.echo("📝 Describing . . .")
    if name:
        target_playlists = [get_named_playlist(name)]
    else:
        target_playlists = get_user_playlists()

    for target_playlist in target_playlists:
        tracks = get_playlist_tracks(target_playlist.uri)
        tracks = set_audio_features(tracks)
        summarized_playlist = PlaylistSummary(playlist=target_playlist, tracks=tracks)
        if output:
            out_file = output / f"{target_playlist.name}.json"
            typer.echo(f"Wrote playlist {target_playlist.name} in {out_file}")
            dump(summarized_playlist, out_file)
        else:
            typer.echo(summarized_playlist)


def main():  # noqa: D103
    typer.run(describe)
