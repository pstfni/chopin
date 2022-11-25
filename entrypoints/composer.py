from pathlib import Path
from typing import Optional

import typer
from ruamel import yaml

from managers.client import ClientManager
from managers.playlist import PlaylistManager
from managers.spotify_client import SpotifyClient
from schemas.composer import ComposerConfig, ComposerConfigItem
from utils import get_logger, simplify_string

LOGGER = get_logger(__name__)


def main(
    nb_songs: Optional[int] = typer.Argument(300, help="Number of songs for the playlist"),
    name: Optional[str] = typer.Argument("🤖 Robot Mix", help="Name for your playlist"),
    composition_config: Optional[Path] = typer.Option(
        None, help="Path to a YAML file with composition for your playlists"
    ),
):
    """Compose a playlist from existing ones.

    You can use a YAML file to specify playlists and artists
    should be used, and weigh them.

    todo: write an how to documentation
    """
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)
    user_playlists = client.get_user_playlists()

    LOGGER.info("🤖 Composing . . .")

    if not composition_config:
        # The user didn't give a config to compose its playlist, we create one from its playlists
        config = ComposerConfig(
            nb_songs=nb_songs,
            playlists=[ComposerConfigItem(name=playlist.name, weight=1) for playlist in user_playlists],
        )

    else:
        config = ComposerConfig.parse_obj(yaml.safe_load(open(composition_config, "r")))

    tracks = playlist_manager.compose(composition_config=config, user_playlists=user_playlists)

    target_playlist = [playlist for playlist in user_playlists if playlist.name == simplify_string(name)]
    if target_playlist:
        playlist = target_playlist[0]
        playlist_manager.replace(uri=playlist.uri, tracks=tracks)

    else:
        playlist = client.create_playlist(name)
        playlist_manager.fill(uri=playlist.uri, tracks=tracks)


if __name__ == "__main__":
    typer.run(main)
