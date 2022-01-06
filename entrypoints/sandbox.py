import argparse
import random
from pathlib import Path
from typing import Dict, List, Optional

import spotipy
from ruamel.yaml import safe_load

from models.client import SpotifyClient
from models.playlist import Playlist
from models.user import User
from utils import get_logger

logger = get_logger(__name__)


def retrieve_playlists(user: User, client: spotipy.Spotify) -> List[Playlist]:
    playlists = user.get_user_playlists()
    return [Playlist(client, playlist) for playlist in playlists]


def compose_playlist(
    playlists: List[Playlist], nb_songs: int = 300, mapping_value: Optional[Dict[str, int]] = None
) -> List[str]:
    """
    Compose a playlist from a list of playlists
    Args:
        playlists: Playlists to pick from
        nb_songs: Target number of songs
        mapping_value: A dictionary with a value assigned to each playlist. Will impact the number of song we pick
        from each playlist.

    Returns:
        A list of track ids.
    """

    default_nb_songs = int(nb_songs / len(playlists))
    target_tracks = []
    for playlist in playlists:
        playlist_tracks = playlist.get_tracks()
        playlist_value = get_playlist_value(playlist.playlist.name, mapping_value)

        nb_tracks_to_add = min(int(default_nb_songs * playlist_value), len(playlist_tracks))
        target_tracks.extend(random.sample(playlist_tracks, nb_tracks_to_add))
    return list(set(target_tracks))


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
    user = User(client)
    user_playlists = retrieve_playlists(user, client)
    playlist = user.create_playlist(name=ARGS["name"])
    playlist_tracks = compose_playlist(user_playlists, nb_songs=ARGS["nb_songs"], mapping_value=playlist_values_dict)

    playlist.fill(playlist_tracks)


if __name__ == "__main__":
    main()
