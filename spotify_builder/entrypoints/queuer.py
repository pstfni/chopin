from typing import Optional

import typer

from spotify_builder.managers.client import ClientManager
from spotify_builder.managers.playlist import PlaylistManager
from spotify_builder.managers.spotify_client import SpotifyClient
from spotify_builder.utils import get_logger, simplify_string

LOGGER = get_logger(__name__)


def main(
    name: Optional[str] = typer.Argument("🔮 Queued Mix", help="Name for your playlist"),
):
    """Create a playlist and shuffle it from the user's queue.

    !!! warning
        Due to Spotify API limits, you must be _playing_ a song on an active device for this to work.

    !!! warning
        Due to Spotify API limits, the maximum number of songs you can use is 20.
    """
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)

    LOGGER.info("🔮 Queuing . . .")

    user_playlists = client.get_user_playlists()
    target_playlist = [playlist for playlist in user_playlists if playlist.name == simplify_string(name)]
    playlist_tracks = client.get_queue()

    if target_playlist:
        playlist = target_playlist[0]
    else:
        playlist = client.create_playlist(name)

    playlist_manager.fill(uri=playlist.uri, tracks=playlist_tracks)


if __name__ == "__main__":
    typer.run(main)
