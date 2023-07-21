"""Create a playlist from the queue entrypoint."""
import typer

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.tools.logger import get_logger

LOGGER = get_logger(__name__)


def queue(
    name: str | None = typer.Argument("🔮 Queued Mix", help="Name for your playlist"),
):
    """Create a playlist and shuffle it from the user's queue.

    !!! warning     Due to Spotify API limits, you must be _playing_ a
    song on an active device for this to work.

    !!! warning     Due to Spotify API limits, the maximum number of
    songs you can use is 20.
    """
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)

    LOGGER.info("🔮 Queuing . . .")
    playlist_manager.create_playlist_from_queue(name)


def main():  # noqa: D103
    typer.run(queue)
