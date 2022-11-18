"""
Module for all things related to the data : parsing, normalization, formatting, ... before ML models
"""
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from schemas.base import TrackData


def read_playlist(playlist_filepath: Path) -> Tuple[str, List[TrackData]]:
    """From a filepath containing a playlist object, read the playlist data and returns a list of tracks.

    Args:
        playlist_filepath: List of paths to .json files, describing playlists.

    Returns:
        A dictionary, describing tracks
    """
    playlist_name = playlist_filepath.stem
    playlist = json.load(open(playlist_filepath, "r"))
    tracks = [TrackData.parse_obj(track) for track in playlist]
    return playlist_name, tracks


def format_track(track: TrackData) -> Dict[str, Any]:
    """Format a track for our ML needs.

    Args:
        track: Current track data

    Returns:
        A dictionary containing the flatten track: its name, the album release date, and music features.
    """
    track = track.to_flatten_dict(
        include={
            "name": True,
            "album": {"release_date"},
            "features": {
                "acousticness",
                "danceability",
                "energy",
                "instrumentalness",
                "liveness",
                "loudness",
                "speechiness",
                "valence",
                "tempo",
            },
        }
    )
    track["album.release_date"] = track["album.release_date"].year
    return track


def format_records(track: TrackData, playlist_name: str, train_test_split: float = 0.8) -> Dict[str, Any]:
    """
    Format the record (a track data and a label - ie a playlist name) for ML experimentation
    Key features are selected here, release year is extracted, and a label is added.

    Args:
        track: Current track data
        playlist_name: Playlist of the associated track
        train_test_split: Associate the track in a train or test split. Defaults: 80% of chance to be in a train split.

    Returns:
        A dictionary, containing the flatten track with useful information.

    Raises:
        ValueError: if the train test split fraction is not between 0 and 1
    """
    if train_test_split <= 0 or train_test_split > 1:
        raise ValueError(f"Train test split given is {train_test_split}. Expected a number between 0 and 1")
    track = format_track(track)
    track.update({"playlist.name": playlist_name})
    track["split"] = "train" if random.random() < train_test_split else "validation"
    return track


def normalize_features(records: pd.DataFrame) -> pd.DataFrame:
    """Normalize the features across the records.

    Args:
        records: A dataframe containing 'features.' columns

    Returns:
        The normalized dataframe
    """
    for column in records.columns:
        if column.startswith("features"):
            denum = records[column].max() - records[column].min()
            records[column] = (records[column] - records[column].min()) / denum if denum != 0 else 0.0
    return records


def split_train_test_records(records: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split a records dataframe into train and validation sets.

    Args:
        records: A dataframe with a 'split' column

    Returns:
        The _shuffled_ 'train' dataframe and the 'test' dataframe.
    """
    mask = records["split"] == "train"
    train_records = records[mask].drop("split", axis=1).sample(frac=1)
    test_records = records[~mask].drop("split", axis=1).sample(frac=1)
    return train_records, test_records


def create_train_records(playlist_filepaths: List[Path]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Read a list of playlists (from their paths) and create dataframe records.

    Args:
        playlist_filepaths: A list of playlist filepaths

    Returns:
        A dataframe ready for training, and a dataframe containing test tracks.
    """
    all_tracks = []
    for playlist in playlist_filepaths:
        name, tracks = read_playlist(playlist)
        tracks = [format_records(track, name) for track in tracks]
        all_tracks.extend(tracks)

    records = pd.DataFrame().from_records(all_tracks)
    records = normalize_features(records)
    return split_train_test_records(records)


def _create_inference_records(tracks: List[Dict[str, Any]]):
    records = pd.DataFrame().from_records(tracks)
    records = records.drop(["playlist.name", "split"], axis=1)
    return records


def create_inference_records_from_paths(playlist_filepaths: List[Path]) -> pd.DataFrame:
    """Read a list of playlist, from their paths, and create dataframe records.

    Args:
        playlist_filepaths: A list of playlist filepaths

    Returns:
        A dataframe ready for inference.
    """
    all_tracks = []
    for playlist in playlist_filepaths:
        name, tracks = read_playlist(playlist)
        tracks = [format_records(track, name) for track in tracks]
        all_tracks.extend(tracks)
    return _create_inference_records(all_tracks)


def create_inference_records_from_tracks(tracks: List[TrackData], name: Optional[str] = "") -> pd.DataFrame:
    """Create dataframe records for inference, based on a list of track data.

    Args:
        tracks: A list of tracks
        name: Optional name for the records you are classifying.

    Returns:
        A dataframe ready for inference
    """
    tracks = [format_records(track, name) for track in tracks]
    return _create_inference_records(tracks)
