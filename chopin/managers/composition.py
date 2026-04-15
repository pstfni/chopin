"""Manage composition."""

import itertools
import random
from datetime import date

from chopin.client.endpoints import (
    get_top_tracks,
    get_user_playlists,
)
from chopin.managers.playlist import (
    tracks_from_playlist_name,
    tracks_from_playlist_uri,
)
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigListeningHistory
from chopin.schemas.track import TrackData
from chopin.sources import get_registry, register
from chopin.tools.logger import get_logger

logger = get_logger(__name__)


# todo: logging decorator
@register("playlists", ComposerConfigItem)
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


@register("history", ComposerConfigListeningHistory)
def _add_from_history(history_ranges: list[ComposerConfigListeningHistory], **kwargs) -> list[TrackData]:
    tracks = [get_top_tracks(time_range=history.time_range, limit=history.nb_songs) for history in history_ranges]
    return list(itertools.chain(*tracks))


@register("uris", ComposerConfigItem)
def _add_from_uris(
    uris: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    tracks = [
        tracks_from_playlist_uri(
            playlist_uri=uri.name,
            nb_tracks=uri.nb_songs,
            release_range=release_range,
            selection_method=uri.selection_method,
        )
        for uri in uris
    ]
    return list(itertools.chain(*tracks))


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

    for key, source in get_registry().items():
        source_config = getattr(composition_config, key, None)
        if not source_config:
            continue
        source_tracks = source.handler(source_config, release_range=composition_config.release_range, tracks=tracks)
        tracks.extend(source_tracks)

    return random.sample(tracks, len(tracks))
