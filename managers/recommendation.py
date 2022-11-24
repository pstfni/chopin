from typing import Dict, List, Optional

import numpy as np

from managers.client import ClientManager
from schemas.base import ArtistData, TrackData, TrackFeaturesData
from utils import get_logger

logger = get_logger(__name__)


def _generate_target_features(target_features: TrackFeaturesData) -> Dict[str, float]:
    """Read the track features data and create a dictionary ready to be sent to the Spotify API. Features without value
    are ignored.

    Args:
        target_features: Track Features

    Returns:
        A dictionary, with target features and their target value.
    """
    return {
        f"target_{feature}": feature_value
        for feature, feature_value in target_features.dict().items()
        if feature_value is not None
    }


class RecommendationManager:
    """Class to manage everything related to Spotify recommendations."""

    def __init__(self, client: ClientManager):
        self.client = client

    def get_recommendations_from_artists(
        self, max_recommendations: int, artists: List[ArtistData], target_features: Optional[TrackFeaturesData] = None
    ) -> List[TrackData]:
        """Retrieve recommendations from artists data.

        !!! Note
            Only 5 artists can be used as a seed. If there are more than 5 artists in the `artists` list, five of
            them will randomly be selected.
            If you want to control the artists used, we recommend to select them before calling the function.

        Args:
            max_recommendations: Number of recommendations to retrieve
            artists: A list of artists data. The artists will be used to generate recommendations.
            target_features: Track features to use to direct recommendations made.

        Returns:
            A list of recommended tracks
        """
        if len(artists) > 5:
            logger.warning("More than 5 artists were passed for the recommendation. We will randomly select 5 of them")
            artists = np.random.choice(artists, 5, replace=False)
        seed = [artist.id for artist in artists]
        target_features = _generate_target_features(target_features) if target_features else {}
        return self.get_recommendations(max_recommendations=max_recommendations, seed_artists=seed, **target_features)

    def get_recommendations_from_tracks(
        self, max_recommendations: int, tracks: List[TrackData], target_features: Optional[TrackFeaturesData] = None
    ) -> List[TrackData]:
        """Retrieve recommendations from track data.

        !!! Note
            Only 5 tracks can be used as a seed. If there are more than 5 tracks in the `tracks` list, five of
            them will randomly be selected.
            If you want to control the tracks used, we recommend to select them before calling the function.

        Args:
            max_recommendations: Number of recommendations to retrieve
            tracks: A list of tracks data. The tracks will be used to generate recommendations.
            target_features: Track features to use to direct recommendations made.

        Returns:
            A list of recommended tracks
        """
        if len(tracks) > 5:
            logger.warning("More than 5 artists were passed for the recommendation. We will randomly select 5 of them")
            tracks = np.random.choice(tracks, 5, replace=False)
        seed = [track.id for track in tracks]
        target_features = _generate_target_features(target_features) if target_features else {}
        return self.get_recommendations(max_recommendations=max_recommendations, seed_tracks=seed, **target_features)

    def get_recommendations(
        self,
        max_recommendations: int,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        **kwargs,
    ) -> List[TrackData]:
        """Get recommendations from a list of artists, tracks, or genres.

        Args:
            seed_artists: Comma separated list of artist ids
            seed_tracks: Comma separated list of track ids
            seed_genres: Comma separated list of genre names
            max_recommendations: Maximum number of tracks to return
            **kwargs: Spotify API kwargs. Notably, target features data can be passed here to tweak the recommendations.
                See `_generate_target_features` for more information

        Returns:
            A list of track data recommended by Spotify, based on the seeds.
        """
        seeds = (
            [] + [artist for artist in seed_artists]
            if seed_artists
            else [] + [track for track in seed_tracks]
            if seed_tracks
            else [] + [genre for genre in seed_genres]
            if seed_genres
            else []
        )
        if len(seeds) > 5:
            raise ValueError(f"{len(seeds)} seeds were given for the recommendation, but Spotify only allow 5 or less.")
        recommendations = self.client.get_recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            limit=max_recommendations,
            **kwargs,
        )["tracks"]
        return [TrackData(**track) for track in recommendations]
