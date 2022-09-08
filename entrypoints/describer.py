from pathlib import Path
from typing import Optional

import typer

from managers.client import SpotifyClient
from managers.playlist import PlaylistManager
from managers.track import TrackManager
from managers.user import UserManager
from utils import get_logger

logger = get_logger(__name__)


def main(
    output: Path = typer.Argument(..., help="Output directory"),
    name: Optional[str] = typer.Argument(
        None, help="Specific name of a playlist to fetch. If none, all playlists are fetched"
    ),
):
    """Retrieve data from a playlist and describe it.

    The playlist(s) (summarized as JSONs) will be written into files in
    the output directory
    """

    client = SpotifyClient().get_client()
    playlist_manager = PlaylistManager(client)
    track_manager = TrackManager(client)
    user = UserManager(client)

    user_playlists = user.get_user_playlists()
    if name:
        target_playlists = [playlist for playlist in user_playlists if name == playlist.name]
    else:
        target_playlists = user_playlists

    for target_playlist in target_playlists:
        out_file = output / f"{target_playlist.name}.json"
        logger.info(f"Describing playlist {target_playlist.name} in {out_file}")
        tracks = playlist_manager.get_tracks(target_playlist.uri)
        tracks = track_manager.set_audio_features(tracks)
        track_manager.dump(tracks, out_file)


if __name__ == "__main__":
    typer.run(main)
