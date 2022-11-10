from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError
from ruamel.yaml import safe_load

from managers.client import ClientManager
from managers.playlist import PlaylistManager
from managers.recommendation import RecommendationManager
from managers.spotify_client import SpotifyClient
from schemas import TrackFeaturesData
from utils import get_logger

LOGGER = get_logger(__name__)
MAX_SEEDS = 5  # Spotify only accepts up to 5 seeds for the recommendation


def main(
    nb_songs: Optional[int] = typer.Argument(100, min=0, max=100, help="Number of songs for the playlist"),
    mode: Optional[str] = typer.Option(
        "hot",
        help=(
            "Timeframe for the recommendations: "
            "'hot' (default) will get tracks and artists from the recent listening habits."
            "'top' will get tracks and artists based on all time numbers"
        ),
    ),
    name: Optional[str] = typer.Argument("💡 Recommended Mix", help="Name for your playlist"),
    target_features_file: Optional[Path] = typer.Option(None, help="Path to a YAML file with target features"),
):
    """Create a playlist from recommendations.

    You can use a YAML file to specify target features. They can help
    finetune the recommendations to your mood.
    """
    target_features = None
    if target_features_file:
        if not Path.is_file(target_features_file):
            raise ValueError(f"Error: {target_features} is not a valid file")
        try:
            target_features = TrackFeaturesData.parse_obj(safe_load(open(target_features_file, "r")))
        except ValidationError as err:
            raise ValueError(f"Content of the file {target_features} did not meet the TrackFeaturesData schema.\n{err}")

    client = ClientManager(SpotifyClient().get_client())
    playlist_manager = PlaylistManager(client)
    recommendation_manager = RecommendationManager(client)

    LOGGER.info("💡 Creating recommendations . . .")

    playlist = client.create_playlist(name, description="Homemade recommendations")
    if nb_songs > 100:
        LOGGER.warning("recommendations mode only allows 100 songs. Reducing the number of songs")
        nb_songs = 100

    artists = client.get_top_artists(MAX_SEEDS) if mode == "top" else client.get_hot_artists(MAX_SEEDS)
    tracks = client.get_top_tracks(MAX_SEEDS) if mode == "top" else client.get_top_tracks(MAX_SEEDS)
    playlist_tracks = recommendation_manager.get_recommendations_from_tracks(
        max_recommendations=nb_songs // 2, tracks=tracks, target_features=target_features
    )
    playlist_tracks += recommendation_manager.get_recommendations_from_artists(
        max_recommendations=nb_songs // 2, artists=artists, target_features=target_features
    )

    playlist_manager.fill(uri=playlist.uri, tracks=playlist_tracks)


if __name__ == "__main__":
    typer.run(main)
