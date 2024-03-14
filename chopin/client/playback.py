"""Spotify API calls for playback related features."""

import requests
import spotipy

from chopin.client.settings import _client
from chopin.schemas.track import TrackData


def get_currently_playing() -> TrackData | None:
    """Get the track being played.

    Returns:
        The track data of the track; or nothing if the user doesn't have an active listening session.
    """
    response = _client.current_playback()
    if not response or response["currently_playing_type"] != "track":
        return None
    return TrackData.model_validate(response["item"])


def get_queue() -> list[TrackData]:
    """Get the current user's listening queue.

    Returns:
        The list of track data in the user's queue.

    Raises:
        ValueError: if the user doesn't have an active (ie: doesn't have a track playing)

    Note:
        API Call has to be custom made, waiting for its implementation in Spotipy.
    """
    if not _client.current_playback().get("is_playing"):
        raise ValueError(
            "Spotify should be active on a device and the playback should be on for the get_queue endpoint to work."
        )

    headers = {
        "Authorization": f"Bearer {_client.auth_manager.get_access_token(as_dict=False)}",
        "Content-Type": "application/json",
    }
    route = "https://api.spotify.com/v1/me/player/queue"
    try:
        response = _client._session.request(
            method="GET",
            url=route,
            headers=headers,
            timeout=5,
            proxies=None,
        )
        response.raise_for_status()
        results = response.json()
    except requests.exceptions.HTTPError as http_error:
        error_response = http_error.response
        raise spotipy.SpotifyException(
            error_response.status_code, -1, f"{route}\n{error_response}", headers=error_response.headers
        ) from http_error
    except ValueError:
        results = None
    return [TrackData(**track) for track in results.get("queue")]
