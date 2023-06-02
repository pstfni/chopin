from typing import Optional

import typer

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.utils import get_logger

LOGGER = get_logger(__name__)


def create_playlist_from_queue(client: ClientManager, name: str):
    """Create a playlist from the user's queue.

    Args:
        client: A Client Manager, for all calls with spotipy
        name: The name of the playlist.

    Todo: Move this somewhere else.
    """
    playlist_manager = PlaylistManager(client)
    playlist = playlist_manager.create(name, overwrite=True)
    tracks = client.get_queue()
    playlist_manager.fill(uri=playlist.uri, tracks=tracks)
    return playlist


def queue(
    name: Optional[str] = typer.Argument("🔮 Queued Mix", help="Name for your playlist"),
):
    """Create a playlist and shuffle it from the user's queue.

    !!! warning
        Due to Spotify API limits, you must be _playing_ a song on an active device for this to work.

    !!! warning
        Due to Spotify API limits, the maximum number of songs you can use is 20.
    """
    client = ClientManager(SpotifyClient().get_client())
    LOGGER.info("🔮 Queuing . . .")
    create_playlist_from_queue(client, name)


def main():
    typer.run(queue)
