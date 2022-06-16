import argparse
from pathlib import Path

from models.client import SpotifyClient
from models.playlist import PlaylistManager
from models.track import TrackManager
from models.user import UserManager
from utils import get_logger

logger = get_logger(__name__)


def main():
    """Retrieve data from a playlist and describe it"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-n", default=None, type=str, help="Name of the playlist to fetch")
    parser.add_argument("--output", "-o", type=Path, help="Output directory to describe the playlist")
    parser.add_argument("--all", "-a", action="store_true", help="Option to retrieve metadata for all the playlists")

    ARGS = vars(parser.parse_args())
    playlist_name = ARGS["name"]
    fetch_all_playlists = ARGS["all"]
    if playlist_name and fetch_all_playlists or (not playlist_name and not fetch_all_playlists):
        raise ValueError("Specify one of 'name' or 'all' options.")

    client = SpotifyClient().get_client()
    playlist_manager = PlaylistManager(client)
    track_manager = TrackManager(client)
    user = UserManager(client)

    user_playlists = user.get_user_playlists()
    if playlist_name:
        target_playlists = [playlist for playlist in user_playlists if ARGS["name"] == playlist.name]
    else:
        target_playlists = user_playlists

    for target_playlist in target_playlists:
        out_file = ARGS["output"] / f"{target_playlist.name}.json"
        logger.info(f"Describing playlist {target_playlist.name} in {out_file}")
        tracks = playlist_manager.get_tracks(target_playlist.uri)
        tracks = track_manager.set_audio_features(tracks)
        track_manager.dump(tracks, out_file)


if __name__ == "__main__":
    main()
