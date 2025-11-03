"""Compose a playlist entrypoint."""

from datetime import datetime, timedelta
from pathlib import Path

import click
from ruamel.yaml import YAML

from chopin.managers.composition import compose_playlist
from chopin.managers.playlist import create, fill
from chopin.schemas.composer import ComposerConfig
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


@click.command()
@click.argument("configuration", type=click.Path(exists=True, path_type=Path))
def compose(
    configuration: Path,
):
    """Compose a playlist from a composition configuration.

    You can use a YAML file to specify playlists and artists should be
    used, and weigh them.
    """
    click.echo("🤖 Composing . . .")

    yaml = YAML(typ="safe", pure=True)
    config = ComposerConfig.model_validate(yaml.load(open(configuration)))

    tracks = compose_playlist(composition_config=config)

    playlist = create(name=config.name, description=config.description, overwrite=True)
    fill(uri=playlist.uri, tracks=tracks)
    click.echo(f"Playlist '{playlist.name}' successfully created.")


def compose_from_new_releases(
    configuration_path: Path = Path("confs/recent.yaml"),
):
    """Compose a playlist based on recent releases.

    Args:
        configuration_path: The composition configuration, `confs/recent.yaml` by default.
    """
    LOGGER.info("🆕 Composing with new releases")
    yaml = YAML(typ="safe", pure=True)
    config = ComposerConfig.model_validate(yaml.load(open(configuration_path)))
    config.release_range = ((datetime.now() - timedelta(days=15)).date(), datetime.now().date())
    tracks = compose_playlist(composition_config=config)

    playlist = create(name=config.name, description=config.description, overwrite=True)
    fill(uri=playlist.uri, tracks=tracks)
    LOGGER.info(f"Playlist '{playlist.name}' successfully created.")
