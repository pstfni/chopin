from pathlib import Path
from typing import Optional

import typer
from ruamel.yaml import safe_load

from managers.client import SpotifyClient
from managers.playlist import PlaylistManager
from managers.user import UserManager
from utils import get_logger

LOGGER = get_logger(__name__)


def main(
    nb_songs: Optional[int] = typer.Argument(300, help="Number of songs for the playlist"),
    name: Optional[str] = typer.Argument("🤖 Robot Mix", help="Name for your playlist"),
    playlist_weights: Optional[Path] = typer.Option(None, help="Path to a YAML file with weights for your playlists"),
):
    """Compose a playlist from existing ones.

    You can use a YAML file to specify which playlist(s) of your profile
    should be used, and weigh them.
    """
    playlist_weights_dict = None
    if playlist_weights:
        if not Path.is_file(playlist_weights):
            raise ValueError(f"Error: {playlist_weights} is not a valid file")
        playlist_weights_dict = safe_load(open(playlist_weights, "r"))

    client = SpotifyClient().get_client()
    playlist_manager = PlaylistManager(client)
    user = UserManager(client)

    LOGGER.info("🤖 Composing . . .")

    user_playlists = user.get_user_playlists()
    playlist = user.create_playlist(name)
    playlist_tracks = playlist_manager.compose(user_playlists, nb_songs, mapping_value=playlist_weights_dict)

    playlist_manager.fill(uri=playlist.uri, tracks=playlist_tracks)


if __name__ == "__main__":
    typer.run(main)
