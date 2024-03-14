"""Operations on spotify tracks."""

import random

import numpy as np

from chopin.client.tracks import get_tracks_audio_features, like_tracks
from chopin.constants import constants
from chopin.schemas.track import TrackData, TrackFeaturesData
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


def get_audio_features(tracks: list[TrackData]) -> list[TrackFeaturesData]:
    """Parse tracks and call Spotify API to retrieve each track's features.

    Args:
        tracks: A list of N TrackData objects for which to retrieve features

    Returns:
        A list of N TrackFeaturesData object.
    """
    uris = [track.uri for track in tracks]
    return get_tracks_audio_features(uris)


def set_audio_features(tracks: list[TrackData]) -> list[TrackData]:
    """Get the features of a list of tracks, and set the `features` attributes to enable later use.

    Args:
        tracks: TrackData objects where you want to read features

    Returns:
        Updated tracks, with features.
    """
    audio_features = get_audio_features(tracks)
    for i in range(len(tracks)):
        tracks[i].features = audio_features[i]
    return tracks


def save_tracks(tracks: list[TrackData]):
    """Add tracks to the current user liked songs.

    Args:
        tracks: Tracks to add
    """
    track_uris = [track.uri for track in tracks]
    like_tracks(track_uris)


def shuffle_tracks(tracks: list[TrackData]) -> list[TrackData]:
    """Shuffle a list of tracks.

    Args:
        tracks: Tracks to shuffle_playlist

    Returns:
        Updated list of tracks
    """
    return random.sample(tracks, len(tracks))


def find_seeds(
    tracks: list[TrackData], feature: str, value: float, nb_seeds: int = constants.SPOTIFY_RECOMMENDATION_SEED_LIMIT
) -> list[TrackData]:
    """For a given feature, find close tracks in a list of tracks.

    !!! example
        Let's say we have the following tracks: ["Robot Rock", "Nightcall", "Pogo", "Imagine", "Into My Arms"], and
        the user wants new songs with high energy. We may want to use "Robot Rock", "Nightcall" or "Pogo" as seeds
        for the new tracks.

    Args:
        tracks: The candidate list of tracks
        feature: The target feature
        value: The target value for the feature
        nb_seeds: The number of track as seeds to return. Defaults to the SPOTIFY API limit for seeds.

    Returns:
        Good candidates for a seed to search for this feature.

    Raises:
        ValueError: if there are no features in the tracks
        ValueError: if the track list is empty
        ValueError: if the feature is not found in the tracks.
    """
    nb_tracks = len(tracks)
    if not nb_tracks:
        raise ValueError("Cannot find good tracks in an empty track list")
    if not tracks[0].features:
        raise ValueError(
            "Features are necessary to use `find_seed`. You may want to `set_audio_features` to add"
            "the Spotify features to your track list"
        )
    features = np.array([getattr(track.features, feature) for track in tracks])
    if (features == None).any():  # noqa: E711
        raise ValueError(f"Could not retrieve feature {feature} for the tracks.")
    target = np.repeat([value], nb_tracks)
    out_size = min(nb_seeds, nb_tracks)
    indexes = np.argpartition(np.abs(features - target), out_size)
    return [tracks[i] for i in indexes[:out_size]]
