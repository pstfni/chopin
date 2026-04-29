"""Manage composition."""

import itertools
import math
import random
import re
from datetime import date

from chopin.client.endpoints import (
    get_top_tracks,
    get_user_playlists,
)
from chopin.managers.playlist import (
    tracks_from_playlist_name,
    tracks_from_playlist_uri,
)
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData
from chopin.tools.logger import get_logger
from chopin.tools.strings import simplify_string

logger = get_logger(__name__)


def _expand_pattern_playlists(
    playlists: list[ComposerConfigItem],
    user_playlists: list[PlaylistData],
) -> list[ComposerConfigItem]:
    """Expand regex patterns in playlist names into individual ComposerConfigItems.

    A pattern is any name containing a regex metacharacter. Each matching user
    playlist becomes its own item, inheriting the original weight and selection
    method. The nb_songs budget is split evenly across all matches.

    Patterns are matched against simplified playlist names (lowercase, no emojis,
    no spaces — see ``simplify_string``). Use ``.*`` to match all playlists, or a
    negative lookahead to exclude specific ones:
    ``^(?!best-of|tmp).*``

    Args:
        playlists: Items from the composer configuration (may contain patterns).
        user_playlists: All playlists available in the user's Spotify library.

    Returns:
        A flat list of items where every pattern has been replaced by its matches.
    """
    expanded = []
    for item in playlists:
        if not re.search(r"[.*+?()\[\]^$|\\]", item.name):
            expanded.append(item)
            continue
        matches = [p for p in user_playlists if re.fullmatch(item.name, simplify_string(p.name))]
        if not matches:
            logger.warning(f"Pattern '{item.name}' matched no playlists — skipping")
            continue
        per_songs = math.ceil(item.nb_songs / len(matches))
        logger.info(f"Pattern '{item.name}' expanded to {len(matches)} playlists: {[p.name for p in matches]}")

        expanded.extend(
            [
                ComposerConfigItem(
                    name=match.name,
                    weight=item.weight,
                    nb_songs=per_songs,
                    selection_method=item.selection_method,
                )
                for match in matches
            ]
        )
    return expanded


# todo: logging decorator
def _add_from_playlists(
    playlists: list[ComposerConfigItem],
    release_range: tuple[date] | None = None,
    added_at_range: tuple[date] | None = None,
    **kwargs,
) -> list[TrackData]:
    """Add tracks from each playlist."""
    user_playlists = get_user_playlists()
    tracks = [
        tracks_from_playlist_name(
            playlist_name=playlist.name,
            nb_tracks=playlist.nb_songs,
            release_range=release_range,
            added_at_range=added_at_range,
            user_playlists=user_playlists,
            selection_method=playlist.selection_method,
        )
        for playlist in _expand_pattern_playlists(playlists, user_playlists)
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
            playlist_uri=uri.name,
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
        source_tracks = DISPATCHER[source](
            source_config,
            release_range=composition_config.release_range,
            added_at_range=composition_config.added_at_range,
            tracks=tracks,
        )
        tracks.extend(source_tracks)

    return random.sample(tracks, len(tracks))
