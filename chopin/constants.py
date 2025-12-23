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
    """Constants namespace for chopin."""

    DEFAULT_DATA_DIR = Path("data/")
    QUEUED_MIX = PlaylistNamedTuple(
        name="🔮 Musique à suivre",
        description="Auto-generated playlist, from the user's queue.",
        nb_songs=20,
    )
    SPOTIFY_USER_URI = "spotify:user:spotify"
    SPOTIFY_API_HISTORY_LIMIT = 50
    SPOTIFY_RECOMMENDATION_SEED_LIMIT = 5
    MARKET = "fr"
    MAX_RELATED_ARTISTS = 10
    MAX_TOP_TRACKS_ARTISTS = 10
    MAX_SEEDS = 5
    TRACK_FIELDS = (
        "total, items.track.id, items.track.name, items.track.uri, items.track.duration_ms, items.track.popularity,"
        "items.track.album.uri, items.track.album.name, items.track.album.release_date, items.track.album.id,"
        "items.track.artists.uri, items.track.artists.name, items.track.artists.id, items.track.artists.genre,"
        "items.added_at"
    )
    """Protected playlists are central to the user and should not be shuffled or deleted.
    Rather, they are the default ones that should be used for composition purposes.
    """
    PROTECTED_PLAYLISTS_ID = [
        "54EDlBcsHHhxlnEZeKyCYK", #rock60s
        "7GwerBM1SrPtUAOQ9yJXWK", #rock70s
        "4KMxj89DO4Gb8doyxIyCEO", #rock80s
        "7JhtLpWqwbemE348CX7auF", #rock90s
        "1SGI7veOH8sO8asYDRGu4m", #rock00s
        "5FgL7uoL2xIEffjK2h83fw", #rock10s
        "5tUUBOx9VIIuz9Envlwywr", #rock20s
        "0tb3osixV9LjfMUQykjlTP", #themes
        "7KhMcAFU21eJ8W2g9bxH5F", #francepop
        "7z6icQ3SqLNOPyiPmOeOd7", #francerock
        "5FXWDxbUTFuqiXFGhEkLZb", #francechill
        "3gtdUSCn5qUxmKBY3j01a6", #chill
        "6bUBLKqs152AsV1C6EEzqp", #ambiance
        "5jP3k93MfPTD1hQVmStf3K", #soul
        "683rt2EivNgqFIS7VwKIPW", #pop
        "6bMNTWMyUAR6Syl8sG6d2M", #hiphop
        "0xf0ro6sNT7LqaacflGaNU", #blues
        "0i9GkLTLvoc1gygu9TTjDB", #electro
        "36g29hGa3gKT5IIrwVTN9n", #best-of2025
        "6pB5rq21baD95XG3NKTWYb", #best-of2024
        "3oZgUL8lf7loC38YyrhNnl", #best-of2023
        "1gKJKtG74Lyc7lb52qON3C", #best-of2022
    ]



constants = ConstantsNamespace()
