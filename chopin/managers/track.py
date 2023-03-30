from typing import List

from chopin.managers.client import ClientManager
from chopin.schemas.base import TrackData, TrackFeaturesData
from chopin.utils import get_logger

logger = get_logger(__name__)


class TrackManager:
    """Class to handle all things related to your Spotify tracks, like getting their features, adding tracks to your
    likes, I/O methods, ..."""

    def __init__(self, client: ClientManager):
        self.client = client

    def get_audio_features(self, tracks: List[TrackData]) -> List[TrackFeaturesData]:
        """Parse tracks and call Spotify API to retrieve each track's features.

        Args:
            tracks: A list of N TrackData objects for which to retrieve features

        Returns:
            A list of N TrackFeaturesData object.
        """
        uris = [track.uri for track in tracks]
        return self.client.get_tracks_audio_features(uris)

    def set_audio_features(self, tracks: List[TrackData]) -> List[TrackData]:
        """Get the features of a list of tracks, and set the `features` attributes to enable later use.

        Args:
            tracks: TrackData objects where you want to read features

        Returns:
            Updated tracks, with features.
        """
        audio_features = self.get_audio_features(tracks)
        for i in range(len(tracks)):
            tracks[i].features = audio_features[i]
        return tracks

    def save_tracks(self, tracks: List[TrackData]):
        """Add tracks to the current user liked songs.

        Args:
            tracks: Tracks to add
        """
        track_uris = [track.uri for track in tracks]
        self.client.like_tracks(track_uris)
