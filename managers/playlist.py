import random
from typing import Dict, List, Optional

import numpy as np
from tqdm import tqdm

from managers.client import ClientManager
from schemas.base import PlaylistData, TrackData
from utils import get_logger

logger = get_logger(__name__)


class PlaylistManager:
    def __init__(self, client: ClientManager):
        """Class to manage all operations related to your playlists. Here you can fill a playlist, replace its tracks,
        compose a playlist ...

        Args:
            client: A ClientManager instance, for all the calls related to the Spotify API.
        """
        self.client = client

    def fill(self, uri: str, tracks: List[TrackData]):
        """Fill a playlist with tracks.

        !!! note
            Duplicate tracks will be removed.

        Args:
            uri: uri of the playlist to fill
            tracks: List of track uuids to add to the playlist
        """
        track_ids = list(set([track.id for track in tracks]))
        self.client.add_tracks_to_playlist(uri, track_ids)

    def replace(self, uri: str, tracks: List[TrackData]):
        """Replace playlist items with new ones.

        Args:
           uri: uri of the playlist to replace
           tracks: List of track uuids to add to the playlist
        """
        track_ids = list(set([track.id for track in tracks]))
        self.client.replace_tracks_in_playlist(uri, track_ids)

    def compose(
        self, playlists: List[PlaylistData], nb_songs: int = 300, mapping_value: Optional[Dict[str, float]] = None
    ) -> List[TrackData]:
        """Compose a playlist from a list of playlists.

        Args:
            playlists: Playlists to pick from
            nb_songs: Target number of songs
            mapping_value: A dictionary with a value assigned to each playlist. Will impact the number of song we pick
            from each playlist.

        Returns:
            A list of track ids.
        """
        if not playlists:
            return []

        if mapping_value:
            playlist_weights = np.array([get_playlist_value(playlist.name, mapping_value) for playlist in playlists])
        else:
            playlist_weights = np.ones(len(playlists))

        default_nb_songs = int(nb_songs / max(len(playlists), 1))
        target_tracks = []
        for playlist, weight in tqdm(zip(playlists, playlist_weights), total=len(playlists)):
            playlist_tracks = self.client.get_tracks(playlist.uri)
            nb_tracks_to_add = min(int(default_nb_songs * weight), len(playlist_tracks))
            target_tracks.extend(random.sample(playlist_tracks, nb_tracks_to_add))
        return target_tracks


def get_playlist_value(name: str, value_mapping: Dict[str, float]) -> float:
    """From a value_mapping dictionary, returns the value of a given playlist name.

    Args:
        name: The name of the playlist
        value_mapping: A dictionary containing a float value for each playlist name.

    !!! note ""
        If the given name is not in the playlist, the value returned will be 0. A warning is also raised.

    Returns:
        The value of the playlist _name_.
    """
    try:
        return value_mapping[name]
    except KeyError:
        logger.warning(f"Warning: {name} not found in the mapping given, will default to a value of 0")
        return 0
