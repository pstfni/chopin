"""Save a playlist (in a serialized JSON)."""

from pathlib import Path

import click

from chopin.client.endpoints import get_named_playlist, get_user_playlists
from chopin.managers.playlist import dump, summarize_playlist
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.argument("output", type=click.Path(exists=True, path_type=Path))
@click.argument("name", type=str)
def backup(
    output: Path,
    name: str,
):
    """Retrieve data from a playlist `name` and save its serialized summary in a file under `output/`."""
    click.echo("📝 Describing . . .")
    if name:
        target_playlists = [get_named_playlist(name)]
    else:
        target_playlists = get_user_playlists()

    for target_playlist in target_playlists:
        summarized_playlist = summarize_playlist(playlist=target_playlist)
        out_file = output / f"{target_playlist.name}.json"
        click.echo(f"Wrote playlist {target_playlist.name} in {out_file}")
        dump(summarized_playlist, out_file)
