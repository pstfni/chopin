"""Compose a playlist with new releases."""
from pathlib import Path

import typer
from ruamel import yaml
from datetime import datetime, timedelta
from chopin.managers.composition import compose

from chopin.managers.playlist import create, fill
from chopin.schemas.composer import ComposerConfig
from chopin.tools.logger import get_logger
from typing import Annotated

LOGGER = get_logger(__name__)


def new_releases(
    composition_config_path: Annotated[
        Path | None, typer.Argument(..., help="Override the configuration with a valid composer configuration")
    ] = None,
):
    """Create a new playlist with recent releases."""

    typer.echo("🆕 Composing with new releases")
    composition_config_path = composition_config_path or Path("confs/recent.yaml")
    config = ComposerConfig.model_validate(yaml.safe_load(open(composition_config_path)))
    config.release_range = ((datetime.now() - timedelta(days=15)).date(), datetime.now().date())
    tracks = compose(composition_config=config, user_playlists=None)

    playlist = create(name=config.name, description=config.description, overwrite=True)
    fill(uri=playlist.uri, tracks=tracks)
    typer.echo(f"Playlist '{playlist.name}' successfully created.")


def main():  # noqa: D103
    typer.run(new_releases)
