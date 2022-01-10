import argparse
from pathlib import Path

from ruamel.yaml import safe_load

from models.client import SpotifyClient
from models.playlist import PlaylistManager
from models.user import User
from utils import get_logger

logger = get_logger(__name__)


def main():
    """Compose a playlist from existing ones"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--nb_songs", "-nb", type=int, default=300, help="Number of songs for the new playlist")
    parser.add_argument("--name", "-n", type=str, default="Robot Mix 🤖", help="Name for your playlist")
    parser.add_argument(
        "--playlist_values", "-p", type=Path, default=None, help="Path to a yaml file with values for your playlists"
    )

    ARGS = vars(parser.parse_args())
    playlist_values_dict = None
    if ARGS["playlist_values"]:
        if not Path.is_file(ARGS["playlist_values"]):
            raise ValueError(f"Error: {ARGS['playlist_values']} is not a valid file")
        playlist_values_dict = safe_load(open(ARGS["playlist_values"], "r"))

    client = SpotifyClient().get_client()
    playlist_manager = PlaylistManager(client)
    user = User(client)
    user_playlists = user.get_user_playlists()
    playlist = user.create_playlist(name=ARGS["name"])
    playlist_tracks = playlist_manager.compose(
        user_playlists, nb_songs=ARGS["nb_songs"], mapping_value=playlist_values_dict
    )

    playlist_manager.fill(uri=playlist.uri, tracks=playlist_tracks)


if __name__ == "__main__":
    main()
