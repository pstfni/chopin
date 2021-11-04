import argparse
from pathlib import Path

from ruamel.yaml import safe_load

from models.client import SpotifyClient
from models.user import User

import composer

parser = argparse.ArgumentParser()
parser.add_argument("--nb_songs", "-nb", type=int, default=300, help="Number of songs for the new playlist")
parser.add_argument("--name", "-n", type=str, default="Robot Mix 🤖", help="Name for your playlist")
parser.add_argument("--playlist_values", "-p", type=Path, default="",
                    help="Path to a yaml file with values for your playlists")

if __name__ == "__main__":
    ARGS = vars(parser.parse_args())

    playlist_values_dict = None
    if ARGS["playlist_values"]:
        assert Path.is_file(ARGS["playlist_values"]), f"Error: {ARGS['playlist_values']} not found"
        playlist_values_dict = safe_load(open(ARGS["playlist_values"], "r"))

    client = SpotifyClient().get_client()
    user = User(client)
    user_playlists = composer.retrieve_playlists(user, client)
    playlist = user.create_playlist(name=ARGS["name"])
    playlist_tracks = composer.compose_playlist(user_playlists,
                                                nb_songs= ARGS["nb_songs"],
                                                mapping_value=playlist_values_dict)

    playlist.fill(playlist_tracks)
