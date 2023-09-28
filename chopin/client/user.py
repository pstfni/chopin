"""Spotify API calls for user related features."""

from functools import lru_cache
from typing import Literal

from chopin.client.settings import _client
from chopin.constants import constants
from chopin.schemas.artist import ArtistData
from chopin.schemas.track import TrackData
from chopin.schemas.user import UserData
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_current_user() -> UserData:
    """Retrieve the current user.

    Returns:
        User data.
    """
    user = _client.current_user()
    return UserData(name=user["display_name"], id=user["id"], uri=user["uri"])


def get_likes() -> list[TrackData]:
    """Get user liked tracks.

    Returns:
        The liked tracks.
    """
    offset = 0
    tracks = []
    while True:
        response = _client.current_user_saved_tracks(limit=20, offset=offset)
        tracks.extend(response.get("items"))
        offset += 20
        if not response.get("next"):
            break
    return [TrackData(**track["track"]) for track in tracks]


def get_top_tracks(time_range: Literal["short_term", "medium_term", "long_term"], limit: int) -> list[TrackData]:
    """Get top tracks for the current user.

    Args:
        time_range: The scope of the 'top' tracks.
        limit: A maximum number of tracks to fetch

     !!! note
        Time range is as follow:
        - short_term: last month
        - medium_term: last 6 months
        - long_term: all time

    !!! note
        There is a Spotify limit for a user's top tracks.
        If `limit` is above, it will be reduced to the accepted number.

    Returns:
        The user top tracks for the given time scope.
    """
    if limit > constants.SPOTIFY_API_HISTORY_LIMIT:
        logger.warning(
            f"Asked for {limit} tracks for {time_range} best songs, "
            f"but Spotify API limits to {constants.SPOTIFY_API_HISTORY_LIMIT}"
        )
        limit = constants.SPOTIFY_API_HISTORY_LIMIT
    response = _client.current_user_top_tracks(limit=limit, time_range=time_range)["items"]
    return [TrackData(**track) for track in response]


def get_top_artists(time_range: Literal["short_term", "medium_term", "long_term"], limit: int) -> list[ArtistData]:
    """Get top artists for the current user.

    Args:
        time_range: The time scope of top artists
        limit: A maximum number of artists to fetch

    Returns:
        The user top artists for the given scope.
    """
    response = _client.current_user_top_artists(limit=limit, time_range=time_range)["items"]
    return [ArtistData(**artist) for artist in response]
