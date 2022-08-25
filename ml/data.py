"""
Module for all things related to the data : parsing, normalization, formatting, ... before ML models
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from schemas import TrackData


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


def format_records(track: TrackData, playlist_name: str, train_test_split: float = 0.8) -> Dict:
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
    track.update({"playlist.name": playlist_name})
    track["album.release_date"] = track["album.release_date"].year
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
            records[column] = (records[column] - records[column].min()) / (
                records[column].max() - records[column].min()
            )
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


def create_inference_records(playlist_filepaths: List[Path]) -> pd.DataFrame:
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
    records = pd.DataFrame().from_records(all_tracks)
    records = normalize_features(records)
    records = records.drop(["playlist.name", "split"], axis=1)
    return records
