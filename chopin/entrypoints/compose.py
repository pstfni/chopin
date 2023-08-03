"""Compose a playlist entrypoint."""
from pathlib import Path

import typer
from ruamel import yaml

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def compose(
    nb_songs: int = typer.Argument(50, help="Number of songs for the playlist"),
    composition_config: Path = typer.Option(None, help="Path to a YAML file with composition for your playlists"),
):
    """Compose a playlist from existing ones.

    You can use a YAML file to specify playlists and artists
    should be used, and weigh them.

    todo: write an how to documentation
    """
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)
    user_playlists = client.get_user_playlists()

    typer.echo("🤖 Composing . . .")

    if not composition_config:
        # The user didn't give a config to compose its playlist, we create one from its playlists
        config = ComposerConfig(
            nb_songs=nb_songs,
            playlists=[ComposerConfigItem(name=playlist.name, weight=1) for playlist in user_playlists],
        )

    else:
        config = ComposerConfig.model_validate(yaml.safe_load(open(composition_config)))

    tracks = playlist_manager.compose(composition_config=config, user_playlists=user_playlists)

    playlist = playlist_manager.create(name=config.name, description=config.description, overwrite=True)
    playlist_manager.fill(uri=playlist.uri, tracks=tracks)
    typer.echo(f"Playlist '{playlist.name}' successfully created.")


def main():  # noqa: D103
    typer.run(compose)
