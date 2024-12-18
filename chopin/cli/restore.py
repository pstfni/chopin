"""Restore entrypoint: create a playlist previously saved."""

import json
from pathlib import Path

import click

from chopin import VERSION
from chopin.managers.playlist import create, fill
from chopin.schemas.playlist import PlaylistSummary
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.argument("new-name", type=str)
def restore(
    path: Path,
    new_name: str,
):
    """Create a playlist based on its serialized version, found in `path`.

    Essentially, use this entrypoint to restore a playlist from a backup.

    The filename will be used for the playlist name. You can give it a new name with the `new-name` parameter.

    !!! Note
        Backups can be created with the `backup` entrypoint.
    """
    json_summary = json.load(open(path))
    summary = PlaylistSummary.model_validate(json_summary)
    if json_summary.get("version") != VERSION:
        logger.warning(
            f"The playlist at {path} was described with chopin {json_summary.get('version')}"
            f"but you are trying to restore it with chopin {VERSION}. Unexpected things could occur."
            f"You can checkout: `git checkout {json_summary.get('version')}"
        )

    if new_name:
        summary.playlist.name = new_name

    click.echo("🔝 Restoring")
    playlist = create(name=summary.playlist.name, description=summary.playlist.description, overwrite=False)
    playlist = fill(playlist.uri, tracks=summary.tracks)
