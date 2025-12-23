"""Spotipy client endpoints."""

import random
from datetime import datetime
from functools import lru_cache
from typing import Any, Literal

from pydantic import ValidationError

from chopin.client.settings import _anon_client, _client
from chopin.constants import constants
from chopin.schemas.artist import ArtistData
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData
from chopin.schemas.user import UserData
from chopin.tools.logger import get_logger
from chopin.tools.strings import match_strings, owner_is_spotify, simplify_string

logger = get_logger(__name__)


def search_artist(artist_name: str) -> ArtistData | None:
    """Search an artist.

    Args:
        artist_name: Name of the artist

    Returns:
        Artist data, if found.
    """
    response = _client.search(q=artist_name, limit=10, type="artist", market="fr")["artists"]
    items = response.get("items")
    matched_artists = [artist for artist in items if match_strings([artist["name"], artist_name])]
    if matched_artists:
        return ArtistData(**matched_artists[0])


def get_artist_top_tracks(artist: ArtistData, max_tracks: int = 20) -> list[TrackData]:
    """Get an artist top tracks.

    Args:
        artist: current artist.
        max_tracks: maximum number of tracks to find.

    Returns:
        A list of track data.
    """
    response = _client.artist_top_tracks(artist_id=artist.id)
    tracks = response["tracks"]
    return [TrackData(**track) for track in random.sample(tracks, min(len(tracks), max_tracks))]


def get_currently_playing() -> TrackData | None:
    """Get the track being played.

    Returns:
        The track data of the track; or nothing if the user doesn't have an active listening session.
    """
    response = _client.current_playback()
    if not response or response["currently_playing_type"] != "track":
        return None
    return TrackData.model_validate(response["item"])


def add_to_queue(track: TrackData) -> None:
    """Add a track to the user's queue.

    Args:
        track: Track to add
    """
    _client.add_to_queue(track.uri)


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

    response = _client.queue()
    return [TrackData(**track) for track in response.get("queue")]


@lru_cache
def get_user_playlists() -> list[PlaylistData]:
    """Retrieve the playlists of the current user.

    Returns:
        A list of playlist data.
    """
    playlists = _client.current_user_playlists().get("items", [])
    return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"], id=p["id"]) for p in playlists]


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
    playlist_id: str, release_date_range: tuple[datetime.date, datetime.date] | None = None
) -> list[TrackData]:
    """Get tracks of a given playlist.

    Args:
        playlist_id: The uri of the playlist.
        release_date_range: A date range; tracks to retrieve must have been released in this range.


    Returns:
        A list of track uuids.
    """
    valid_client = _anon_client if owner_is_spotify(playlist_id) else _client

    offset: int = 0
    tracks: list[TrackData] = []
    response: dict[str, Any] = {"response": []}

    while response:
        response = valid_client.playlist_items(
            playlist_id,
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
                if release_date_range[0].date() <= track.album.release_date <= release_date_range[1].date()
            ]
        tracks.extend(response_tracks)

        if len(response["items"]) == 0:
            break
    return tracks


def create_user_playlist(user_id: str, name: str, description: str = "Playlist created with Chopin") -> PlaylistData:
    """Create a playlist in the user library.

    Args:
        user_id: ID of the user for which to add a playlist
        name: Name for the playlist
        description: Optional description for the playlist

    Returns:
        Created playlist data.
    """
    playlist = _client.user_playlist_create(user=user_id, name=name, description=description)
    return PlaylistData(name=playlist["name"], uri=playlist["uri"], id=playlist["id"])


def add_tracks_to_playlist(playlist_id: str, track_ids: list[str]) -> None:
    """Add tracks to a user playlist.

    Args:
        playlist_id: URI of the target playlist
        track_ids: IDs for the tracks.
    """
    paginated_tracks = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
    for page_tracks in paginated_tracks:
        _client.playlist_add_items(playlist_id, page_tracks)


def replace_tracks_in_playlist(playlist_id: str, track_ids: list[str]) -> None:
    """Replace tracks in a given playlist.

    Args:
        playlist_id: URI of the target playlist. All of its tracks will be removed!
        track_ids: New tracks to add in the playlist.
    """
    tracks_to_remove = get_playlist_tracks(playlist_id)
    tracks_to_remove_ids = [track.id for track in tracks_to_remove]
    paginated_tracks = [tracks_to_remove_ids[i : i + 99] for i in range(0, len(tracks_to_remove_ids), 99)]
    for page_tracks in paginated_tracks:
        _client.playlist_remove_all_occurrences_of_items(playlist_id, page_tracks)
    add_tracks_to_playlist(playlist_id, track_ids)


def like_tracks(track_uris: list[str]) -> None:
    """Add tracks to the user' library.

    Args:
        track_uris: Tracks to save.
    """
    _client.current_user_saved_tracks_add(track_uris)


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
