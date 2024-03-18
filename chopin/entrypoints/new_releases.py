"""Compose a playlist with new releases."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated

import typer
from ruamel.yaml import YAML

from chopin.managers.composition import compose
from chopin.managers.playlist import create, fill
from chopin.schemas.composer import ComposerConfig
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def new_releases(
    composition_config_path: Annotated[
        Path | None, typer.Argument(..., help="Override the configuration with a valid composer configuration")
    ] = None,
):
    """Create a new playlist with recent releases."""
    typer.echo("🆕 Composing with new releases")
    composition_config_path = composition_config_path or Path("confs/recent.yaml")
    yaml = YAML(typ="safe", pure=True)
    config = ComposerConfig.model_validate(yaml.load(open(composition_config_path)))
    config.release_range = ((datetime.now() - timedelta(days=15)).date(), datetime.now().date())
    tracks = compose(composition_config=config)

    playlist = create(name=config.name, description=config.description, overwrite=True)
    fill(uri=playlist.uri, tracks=tracks)
    typer.echo(f"Playlist '{playlist.name}' successfully created.")


def main():  # noqa: D103
    typer.run(new_releases)
