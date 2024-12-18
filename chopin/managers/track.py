"""Operations on spotify tracks."""

import random

from chopin.client.endpoints import like_tracks
from chopin.schemas.track import TrackData
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


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
