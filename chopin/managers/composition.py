"""Manage composition."""

import itertools
import random
from datetime import date

from chopin.client.playlists import get_user_playlists
from chopin.client.user import get_top_tracks
from chopin.managers.playlist import (
    tracks_from_artist_name,
    tracks_from_feature_name,
    tracks_from_genre,
    tracks_from_playlist_name,
    tracks_from_playlist_uri,
    tracks_from_radio,
)
from chopin.managers.track import find_seeds, set_audio_features
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
        )
        for playlist in playlists
    ]
    return list(itertools.chain(*tracks))


def _add_from_artists(
    artists: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    tracks = [
        tracks_from_artist_name(artist_name=artist.name, nb_tracks=artist.nb_songs, release_range=release_range)
        for artist in artists
    ]
    return list(itertools.chain(*tracks))


def _add_from_history(history_ranges: list[ComposerConfigItem], **kwargs) -> list[TrackData]:
    tracks = [get_top_tracks(time_range=history.time_range, limit=history.nb_songs) for history in history_ranges]
    return list(itertools.chain(*tracks))


def _add_from_radios(radios: list[ComposerConfigItem], **kwargs) -> list[TrackData]:
    tracks = [tracks_from_radio(artist_name=radio.name, nb_tracks=radio.nb_songs) for radio in radios]
    return list(itertools.chain(*tracks))


def _add_from_uris(
    uris: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    tracks = [
        tracks_from_playlist_uri(playlist_uri=uri.name, nb_tracks=uri.nb_songs, release_range=release_range)
        for uri in uris
    ]
    return list(itertools.chain(*tracks))


def _add_from_genres(
    genres: list[ComposerConfigItem], release_range: tuple[date] | None = None, **kwargs
) -> list[TrackData]:
    return [
        tracks_from_genre(genre=genre.name, nb_tracks=genre.nb_songs, release_range=release_range) for genre in genres
    ]


def _add_from_features(features: list[ComposerConfigItem], tracks: list[TrackData], **kwargs) -> list[TrackData]:
    tracks = set_audio_features(tracks)
    for feature in features:
        seed_tracks = find_seeds(tracks, feature.name, feature.value, feature.nb_songs)
        tracks.extend(
            tracks_from_feature_name(
                seeds=seed_tracks,
                feature_name=feature.name,
                feature_value=feature.value,
                nb_tracks=feature.nb_songs,
            )
        )
    return tracks


DISPATCHER: dict[str, callable] = {
    "playlists": _add_from_playlists,
    "artists": _add_from_artists,
    "features": _add_from_features,
    "history": _add_from_history,
    "genres": _add_from_genres,
    "radios": _add_from_radios,
    "uris": _add_from_uris,
}


def compose(composition_config: ComposerConfig) -> list[TrackData]:
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
