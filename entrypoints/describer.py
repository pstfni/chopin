from pathlib import Path
from typing import Optional

import typer

from managers.client import ClientManager
from managers.playlist import PlaylistManager
from managers.spotify_client import SpotifyClient
from managers.track import TrackManager
from schemas.base import PlaylistSummary
from utils import get_logger

logger = get_logger(__name__)


def main(
    output: Optional[Path] = typer.Argument(None, help="Output directory"),
    name: Optional[str] = typer.Argument(
        None, help="Specific name of a playlist to fetch. If none, all playlists are fetched"
    ),
):
    """Retrieve data from a playlist and describe it.

    The playlist(s) (summarized as JSONs) will be written into files.
    """

    client = ClientManager(SpotifyClient().get_client())
    track_manager = TrackManager(client)
    playlist_manager = PlaylistManager(client)

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
            logger.info(f"Describing playlist {target_playlist.name} in {out_file}")
            playlist_manager.dump(summarized_playlist, out_file)
        else:
            print(summarized_playlist)


if __name__ == "__main__":
    typer.run(main)
