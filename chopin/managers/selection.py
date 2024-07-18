"""Methods and classes to select tracks from a track list.

!!! note "todo"     Move the min(nb_tracks) logic to the main select
function.     With this we should be able to replace the random and
original functions with lambdas.
"""

from enum import Enum

import numpy as np

from chopin.schemas.track import TrackData


class SelectionMethod(str, Enum):
    """Methods available for selection."""

    RANDOM = "random"
    POPULARITY = "popularity"
    LATEST = "latest"
    ORIGINAL = "original"


def _select_random_tracks(tracks: list[TrackData], nb_tracks: int) -> list[TrackData]:
    """Pick nb_tracks out of tracks, randomly.

    Args:
        tracks: Original source of tracks.
        nb_tracks: The number of tracks to pick.

    Returns:
        Selected tracks.
    """
    return np.random.choice(tracks, min(nb_tracks, len(tracks)), replace=False)


def _select_original_tracks(tracks: list[TrackData], nb_tracks: int) -> list[TrackData]:
    """Pick the first nb_tracks of a tracks list.

    Args:
        tracks: Original source of tracks.
        nb_tracks: THe number of tracks to pick.

    Returns:
        Selected tracks.
    """
    return tracks[: min(nb_tracks, len(tracks))]


def _select_popular_tracks(tracks: list[TrackData], nb_tracks: int) -> list[TrackData]:
    """Pick the most popular tracks from tracks.

    Args:
        tracks: Original source of tracks.
        nb_tracks: The number of tracks to pick.

    Returns:
        Selected tracks.
    """
    tracks = sorted(tracks, key=lambda x: x.popularity, reverse=True)
    return tracks[: min(nb_tracks, len(tracks))]


def _select_latest_tracks(tracks: list[TrackData], nb_tracks: int) -> list[TrackData]:
    """Select nb_tracks based on the most recent release dates.

    Args:
        tracks: Original source of tracks.
        nb_tracks: The number of tracks to pick.

    Returns:
        Selected tracks.
    """
    tracks = sorted(tracks, key=lambda x: x.album.release_date, reverse=True)
    return tracks[: min(nb_tracks, len(tracks))]


SELECTION_MAPPER: dict[SelectionMethod, callable] = {
    SelectionMethod.RANDOM: _select_random_tracks,
    SelectionMethod.POPULARITY: _select_popular_tracks,
    SelectionMethod.LATEST: _select_latest_tracks,
    SelectionMethod.ORIGINAL: _select_original_tracks,
}


def select_tracks(
    tracks: list[TrackData], nb_tracks: int, selection_method: SelectionMethod | None = SelectionMethod.RANDOM
) -> list[TrackData]:
    """Select nb_tracks from a list of tracks, using the given rule.

    See SelectionMethod for the available rules.

    Args:
        tracks: Original source of tracks.
        nb_tracks: The number of tracks to pick.
        selection_method: The selection method to use.

    Returns:
        Selected tracks.
    """
    if not selection_method:
        selection_method = SelectionMethod.RANDOM
    return SELECTION_MAPPER[selection_method](tracks=tracks, nb_tracks=nb_tracks)
