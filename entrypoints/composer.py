from pathlib import Path
from typing import Optional

import typer
from ruamel.yaml import safe_load

from managers.client import ClientManager
from managers.playlist import PlaylistManager
from managers.spotify_client import SpotifyClient
from utils import get_logger, simplify_string

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

    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)

    LOGGER.info("🤖 Composing . . .")

    user_playlists = client.get_user_playlists()
    playlist_tracks = playlist_manager.compose(user_playlists, nb_songs, mapping_value=playlist_weights_dict)

    target_playlist = [playlist for playlist in user_playlists if playlist.name == simplify_string(name)]
    if target_playlist:
        playlist = target_playlist[0]
        playlist_manager.replace(uri=playlist.uri, tracks=playlist_tracks)

    else:
        playlist = client.create_playlist(name)
        playlist_manager.fill(uri=playlist.uri, tracks=playlist_tracks)


if __name__ == "__main__":
    typer.run(main)
