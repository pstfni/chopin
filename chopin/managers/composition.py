"""Manage composition."""

import itertools
import random
from datetime import date

from chopin.client.endpoints import get_top_tracks, get_user_playlists
from chopin.managers.playlist import (
    tracks_from_playlist_name,
    tracks_from_playlist_uri,
)
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem
from chopin.schemas.track import TrackData
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


# todo: logging decorator
def _add_from_playlists(
    playlists: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    """Add tracks from each playlist."""
    tracks = [
        tracks_from_playlist_name(
            playlist_name=playlist.name,
            nb_tracks=playlist.nb_songs,
            release_range=release_range,
            user_playlists=get_user_playlists(),
            selection_method=playlist.selection_method,
        )
        for playlist in playlists
    ]
    return list(itertools.chain(*tracks))


def _add_from_history(history_ranges: list[ComposerConfigItem], **kwargs) -> list[TrackData]:
    tracks = [get_top_tracks(time_range=history.time_range, limit=history.nb_songs) for history in history_ranges]
    return list(itertools.chain(*tracks))


def _add_from_uris(
    uris: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    tracks = [
        tracks_from_playlist_uri(
            playlist_id=uri.name,
            nb_tracks=uri.nb_songs,
            release_range=release_range,
            selection_method=uri.selection_method,
        )
        for uri in uris
    ]
    return list(itertools.chain(*tracks))


DISPATCHER: dict[str, callable] = {
    "playlists": _add_from_playlists,
    "history": _add_from_history,
    "uris": _add_from_uris,
}


def compose_playlist(composition_config: ComposerConfig) -> list[TrackData]:
    """From a composition configuration, compose a playlist.

    Args:
        composition_config: A configuration, with playlists, artists, and/or features
            that should be used to create the playlist.

    Returns:
        A list of track data, the tracks to be added to your playlist. The tracks are shuffled.

    Raises:
        AttributeError: if 'playlists' are in the configuration but user_playlists is not passed.
    """
    tracks: list[TrackData] = []

    for source, source_config in composition_config.items:
        if not source_config:
            continue
        source_tracks = DISPATCHER[source](source_config, release_range=composition_config.release_range, tracks=tracks)
        tracks.extend(source_tracks)

    return random.sample(tracks, len(tracks))
