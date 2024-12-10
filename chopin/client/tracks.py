"""Spotify API calls to retrieve tracks related objects."""

from chopin.client.settings import _client


def like_tracks(track_uris: list[str]) -> None:
    """Add tracks to the user' library.

    Args:
        track_uris: Tracks to save.
    """
    _client.current_user_saved_tracks_add(track_uris)
