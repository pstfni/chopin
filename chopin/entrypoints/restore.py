"""Restore entrypoint: create a playlist previously saved."""
import json
from pathlib import Path

import typer

from chopin import VERSION
from chopin.managers.playlist import create, fill
from chopin.schemas.playlist import PlaylistSummary
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


def restore(
    path: Path = typer.Argument(..., help="Path to the summary of the playlist to restore."),
    name: str = typer.Option(None, help="Override the name of the playlist to restore"),
):
    """Create a playlist based on its summary. Essentially, use this entrypoint to restore a playlist from a backup.

    !!! Note
        Backups can be created with the `describe` entrypoint.
    """
    json_summary = json.load(open(path))
    summary = PlaylistSummary.model_validate(json_summary)
    if json_summary.get("version") != VERSION:
        logger.warning(
            f"The playlist at {path} was described with chopin {json_summary.get('version')}"
            f"but you are trying to restore it with chopin {VERSION}. Unexpected things could occur."
            f"You can checkout: `git checkout {json_summary.get('version')}"
        )

    if name:
        summary.playlist.name = name

    typer.echo("🔝 Restoring")
    playlist = create(name=summary.playlist.name, description=summary.playlist.description, overwrite=False)
    playlist = fill(playlist.uri, tracks=summary.tracks)


def main():  # noqa: D103
    typer.run(restore)
