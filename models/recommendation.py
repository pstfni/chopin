from typing import List, Optional

import spotipy

from schemas import TrackData
from utils import get_logger

logger = get_logger(__name__)


class RecommendationManager:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client

    def get_recommendations(
        self,
        max_recommendations: int,
        seed_artists: Optional[List[str]] = None,
        seed_tracks: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
    ) -> List[TrackData]:
        """
        Get recommendations from a list of
        Args:
            seed_artists: Comma separated list of artist ids
            seed_tracks: Comma separated list of track ids
            seed_genres: Comma separated list of genre names
            max_recommendations: Maximum number of tracks to return

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
        response = self.client.recommendations(
            seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, limit=max_recommendations
        )["tracks"]
        return [TrackData(**track) for track in response]
