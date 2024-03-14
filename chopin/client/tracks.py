"""Spotify API calls to retrieve tracks related objects."""

from typing import Any

from chopin.client.settings import _client
from chopin.schemas.track import TrackData, TrackFeaturesData


def get_tracks_audio_features(track_ids: list[str]) -> list[TrackFeaturesData]:
    """Retrieve audio features data for the given list of tracks.

    Args:
        track_ids: Track ids to compute audio features for.

    Returns:
        The list of track features data.
    """
    audio_features: list[dict[str, Any]] = []
    paginated_uris = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
    for page_uris in paginated_uris:
        audio_features.extend(_client.audio_features(page_uris))
    return [TrackFeaturesData(**feature) for feature in audio_features]


def like_tracks(track_uris: list[str]) -> None:
    """Add tracks to the user' library.

    Args:
        track_uris: Tracks to save.
    """
    _client.current_user_saved_tracks_add(track_uris)


def get_recommendations(
    seed_artists: list[str],
    seed_genres: list[str],
    seed_tracks: list[str],
    limit: int,
    **kwargs: Any,
) -> list[TrackData]:
    """Get track recommendations, from various seeds.

    Args:
        seed_artists: Artist seeds (as ids)
        seed_genres:, Genre seeds (as names)
        seed_tracks: Track seeds (as ids)
        limit: A number of recommendations to fetch
        **kwargs: Keyword parameters

    Returns:
        The recommended tracks data.
    """
    response = _client.recommendations(seed_artists, seed_genres, seed_tracks, limit, **kwargs)["tracks"]
    return [TrackData(**track) for track in response]
