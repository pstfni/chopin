import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import spotipy
from pydantic.json import pydantic_encoder
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from schemas import TrackData, TrackFeaturesData
from utils import get_logger

logger = get_logger(__name__)


class TrackManager:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client

    def get_audio_features(self, uris: List[str]) -> List[Dict[str, Any]]:
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

    def save_tracks(self, tracks: List[TrackData]):
        track_uris = [track.uri for track in tracks]
        self.client.current_user_saved_tracks_add(track_uris)

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

    @staticmethod
    def compute_tsne(tracks: List[TrackData]) -> np.ndarray:
        """Compute TSNE over the track data, using their features.

        Args:
            tracks: A list of tracks.

        !!! warning ""
            Features should have already been fetched (using `set_audio_features` for example)

        Returns:
            2D projection of the tracks

        Raises:
            ValueError: if there are not enough tracks for the TSNE computation. >=2 tracks are needed
        """
        tracks_features = [
            list(track.features.dict(exclude={"analysis_url", "key", "mode", "tempo", "loudness"}).values())
            for track in tracks
            if track.features
        ]
        if len(tracks_features) < 2:
            raise ValueError("Not enough track features available to compute the TSNE.")
        scaled_features = StandardScaler().fit_transform(tracks_features)
        return TSNE(n_components=2, learning_rate="auto", init="random").fit_transform(scaled_features)
