import json
from pathlib import Path
from typing import List

import spotipy
from pydantic.json import pydantic_encoder

from schemas import TrackData, TrackFeaturesData
from utils import get_logger

logger = get_logger(__name__)


class TrackManager:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client

    def get_audio_features(self, uris: List[str]) -> List[TrackFeaturesData]:
        audio_features: List[TrackFeaturesData] = []
        paginated_uris = [uris[i : i + 99] for i in range(0, len(uris), 99)]
        for page_uris in paginated_uris:
            audio_features.extend(self.client.audio_features(page_uris))
        return audio_features

    def set_audio_features(self, tracks: List[TrackData]) -> List[TrackData]:
        paginated_tracks = [tracks[i : i + 99] for i in range(0, len(tracks), 99)]
        for page_tracks in paginated_tracks:
            uris = [track.uri for track in page_tracks]
            audio_features = self.get_audio_features(uris)
            for i in range(len(page_tracks)):
                page_tracks[i].features = TrackFeaturesData.parse_obj(audio_features[i])
        return tracks

    def dump(self, tracks: List[TrackData], filepath: Path):
        """
        Dump a list of track in a JSON format
        Args:
            tracks: A list of track data
            filepath: Target file to receive the json dump
        """
        json_str = json.dumps(tracks, default=pydantic_encoder)
        with open(filepath, "w") as f:
            f.write(json_str)
