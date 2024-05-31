"""Constant variables for Chopin."""

from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple


class PlaylistNamedTuple(NamedTuple):
    """Small named tuple for information related to a playlist configuration.

    Attributes:
        name: default name for a playlist
        description: default description for a playlist
        nb_songs: default nb songs for a playlist
    """

    name: str
    description: str
    nb_songs: int


@dataclass(frozen=True)
class ConstantsNamespace:
    DEFAULT_DATA_DIR = Path("data/")

    RECOMMENDED_MIX = PlaylistNamedTuple(
        name="💡 Musique Recommandée",
        description="Auto-generated playlist. Filled with recommendations",
        nb_songs=100,
    )
    QUEUED_MIX = PlaylistNamedTuple(
        name="🔮 Musique à suivre",
        description="Auto-generated playlist, from the user's queue.",
        nb_songs=20,
    )
    SPOTIFY_USER_URI = "spotify:user:spotify"
    SPOTIFY_API_HISTORY_LIMIT = 50
    SPOTIFY_RECOMMENDATION_SEED_LIMIT = 5
    MAX_RELATED_ARTISTS = 10
    MAX_TOP_TRACKS_ARTISTS = 10
    MAX_SEEDS = 5
    TRACK_FIELDS = (
        "total, items.track.id, items.track.name, items.track.uri, items.track.duration_ms, items.track.popularity,"
        "items.track.album.uri, items.track.album.name, items.track.album.release_date, items.track.album.id,"
        "items.track.artists.uri, items.track.artists.name, items.track.artists.id, items.track.artists.genre,"
        "items.added_at"
    )


constants = ConstantsNamespace()
