import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from pydantic.json import pydantic_encoder
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from managers.client import ClientManager
from schemas.base import TrackData, TrackFeaturesData
from utils import get_logger

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

    @staticmethod
    def dump(tracks: List[TrackData], filepath: Path):
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
        tracks_features = [track.features.dict() for track in tracks if track.features]
        if len(tracks_features) < 2:
            raise ValueError("Not enough track features available to compute the TSNE.")

        tracks_features = pd.DataFrame.from_records(tracks_features)
        tracks_features = tracks_features.drop("analysis_url", axis=1)
        scaled_features = StandardScaler().fit_transform(tracks_features)
        return TSNE(n_components=2, learning_rate="auto", init="random").fit_transform(scaled_features)
