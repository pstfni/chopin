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
        uris = [track.uri for track in tracks]
        return self.client.get_tracks_audio_features(uris)

    def set_audio_features(self, tracks: List[TrackData]) -> List[TrackData]:
        audio_features = self.get_audio_features(tracks)
        for i in range(len(tracks)):
            tracks[i].features = audio_features[i]
        return tracks

    def save_tracks(self, tracks: List[TrackData]):
        track_uris = [track.uri for track in tracks]
        self.client.like_tracks(track_uris)
