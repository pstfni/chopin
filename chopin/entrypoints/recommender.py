from typing import Optional

import typer

from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.utils import get_logger

LOGGER = get_logger(__name__)
MAX_SEEDS = 5  # Spotify only accepts up to 5 seeds for the recommendation


def main(
    nb_songs: Optional[int] = typer.Argument(100, min=0, max=100, help="Number of songs for the playlist"),
    name: Optional[str] = typer.Argument("💡 Recommended Mix", help="Name for your playlist"),
):
    """Create a playlist from recommendations.

    You can use a YAML file to specify target features. They can help
    finetune the recommendations to your mood.
    """
    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)
    playlist_manager.create_playlist_from_recommendations(name, nb_songs)


if __name__ == "__main__":
    typer.run(main)
