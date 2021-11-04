import random
import spotipy
from typing import Dict, List, Optional

from models.playlist import Playlist
from models.user import User
from utils import get_logger

logger = get_logger(__name__)


def get_playlist_value(name: str, value_mapping: Dict[str, int]) -> int:
    if value_mapping is None:
        return 1
    else:
        try:
            return value_mapping[name]
        except KeyError:
            logger.warning(f"Warning: {name} not found in the mapping given, will default to a value of 1")
            return 1


def retrieve_playlists(user: User, client: spotipy.Spotify) -> List[Playlist]:
    playlists = user.get_user_playlists()
    return [Playlist(client, playlist) for playlist in playlists]


def compose_playlist(playlists: List[Playlist], nb_songs: int = 300, mapping_value: Optional[Dict[str, int]] = None)\
        -> List[str]:
    """
    Compose a playlist from a list of playlists
    Args:
        playlists: Playlists to pick from
        nb_songs: Target number of songs
        mapping_value: A dictionary with a value assigned to each playlist. Will impact the number of song we pick
        from each playlist.

    Returns:
        A list of track ids.
    """

    default_nb_songs = int(nb_songs / len(playlists))
    target_tracks = []
    for playlist in playlists:
        playlist_tracks = playlist.get_tracks()
        playlist_value = get_playlist_value(playlist.playlist.name, mapping_value)

        nb_tracks_to_add = min(int(default_nb_songs * playlist_value), len(playlist_tracks))
        target_tracks.extend(random.sample(playlist_tracks, nb_tracks_to_add))
    return list(set(target_tracks))
