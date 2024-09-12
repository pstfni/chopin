"""Spotify calls to retrieve playlist-related objects."""

from datetime import datetime
from functools import lru_cache
from typing import Any

from pydantic import ValidationError

from chopin.client.settings import _client
from chopin.client.user import get_current_user
from chopin.constants import constants
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData
from chopin.tools.logger import get_logger
from chopin.tools.strings import simplify_string

logger = get_logger(__name__)


@lru_cache
def get_user_playlists() -> list[PlaylistData]:
    """Retrieve the playlists of the current user.

    Returns:
        A list of playlist data.
    """
    playlists = _client.current_user_playlists().get("items", [])
    return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]


def get_named_playlist(name: str) -> PlaylistData:
    """Find a user playlist based on its name.

    Args:
        name: A string identifying the playlist name

    Returns:
        The playlist data

    Raises:
        ValueError: the playlist `name` was not found.
    """
    playlists = get_user_playlists()
    names = [simplify_string(p.name) for p in playlists]
    try:
        index_ = names.index(simplify_string(name))
    except ValueError as exc:
        raise ValueError(f"Couldn't find playlist {name} in user playlists") from exc
    return playlists[index_]


def _validate_single_track(track: dict[str, Any]) -> TrackData | None:
    """Validate a single track, otherwise log an error.

    Useful against non synced Spotify tracks, which can cause downstream errors.

    Args:
        track: A track, as received after the Spotify API call.

    Returns:
        The validated track if the track was well formatted.
    """
    if not track.get("track"):
        return None
    try:
        validated_track = TrackData.model_validate(dict(added_at=track.get("added_at"), **track["track"]))
        return validated_track
    except ValidationError as exc:
        logger.warning(f"Error in track validation, the track is ignored: {track} \n Exception raised: {exc}")


def _validate_tracks(tracks: list[dict[str, Any]]) -> list[TrackData]:
    """Read and validate track objects from the Spotify response."""
    response_tracks = [_validate_single_track(track) for track in tracks]
    return [track for track in response_tracks if track]


def get_playlist_tracks(
    playlist_uri: str, release_date_range: tuple[datetime.date, datetime.date] | None = None
) -> list[TrackData]:
    """Get tracks of a given playlist.

    Args:
        playlist_uri: The uri of the playlist.
        release_date_range: A date range; tracks to retrieve must have been released in this range.


    Returns:
        A list of track uuids.
    """
    offset: int = 0
    tracks: list[TrackData] = []
    response: dict[str, Any] = {"response": []}

    while response:
        response = _client.playlist_items(
            playlist_uri,
            offset=offset,
            fields=constants.TRACK_FIELDS,
            additional_types=["track"],
        )
        offset += len(response["items"])

        response_tracks = _validate_tracks(response["items"])
        if release_date_range:
            response_tracks = [
                track
                for track in response_tracks
                if release_date_range[0] <= track.album.release_date <= release_date_range[1]
            ]
        tracks.extend(response_tracks)

        if len(response["items"]) == 0:
            break
    return tracks


def create_playlist(name: str, description: str = "Playlist created with Chopin") -> PlaylistData:
    """Create a playlist in the user library.

    Args:
        name: Name for the playlist
        description: Optional description for the playlist

    Returns:
        Created playlist data.
    """
    user = get_current_user()
    playlist = _client.user_playlist_create(user=user.id, name=name, description=description)
    return PlaylistData(name=playlist["name"], uri=playlist["uri"])


def add_tracks_to_playlist(playlist_uri: str, track_ids: list[str]) -> None:
    """Add tracks to a user playlist.

    Args:
        playlist_uri: URI of the target playlist
        track_ids: IDs for the tracks.
    """
    paginated_tracks = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
    for page_tracks in paginated_tracks:
        _client.playlist_add_items(playlist_uri, page_tracks)


def replace_tracks_in_playlist(playlist_uri: str, track_ids: list[str]) -> None:
    """Replace tracks in a given playlist.

    Args:
        playlist_uri: URI of the target playlist. All of its tracks will be removed!
        track_ids: New tracks to add in the playlist.
    """
    tracks_to_remove = get_playlist_tracks(playlist_uri)
    tracks_to_remove_ids = [track.id for track in tracks_to_remove]
    paginated_tracks = [tracks_to_remove_ids[i : i + 99] for i in range(0, len(tracks_to_remove_ids), 99)]
    for page_tracks in paginated_tracks:
        _client.playlist_remove_all_occurrences_of_items(playlist_uri, page_tracks)
    add_tracks_to_playlist(playlist_uri, track_ids)
