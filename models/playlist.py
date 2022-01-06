from typing import Any, Dict, Optional, List

import spotipy
import random

from schemas import PlaylistData
from utils import get_logger

logger = get_logger(__name__)


class PlaylistManager:
    def __init__(self, client: spotipy.Spotify):
        self.client = client

    def get_tracks(self, uri: str) -> List[str]:
        """
        Get tracks of a given playlist
        Args:
            uri: The uri of the playlists

        Returns:
        A list of track uuids.
        """
        # todo: return TrackData
        offset: int = 0
        tracks: List[str] = []
        response: Dict[str, Any] = {"response": []}

        while response:
            response = self.client.playlist_items(
                uri, offset=offset, fields="items.track.id,total", additional_types=["track"]
            )
            offset += len(response["items"])
            response_tracks = [r["track"]["id"] for r in response["items"]]
            tracks.extend(response_tracks)

            if len(response["items"]) == 0:
                break
        return tracks

    def fill(self, uri: str, tracks: List[str]):
        """
        Fill a playlist
        Args:
            uri: uri of the playlist to fill
            tracks: List of track uuids to add to the playlisy

        Returns:

        """
        paginated_tracks = [tracks[i: i + 99] for i in range(0, len(tracks), 99)]
        for page_tracks in paginated_tracks:
            self.client.playlist_add_items(uri, page_tracks)

    def compose(self, playlists: List[PlaylistData], nb_songs: int = 300, mapping_value: Optional[Dict[str, int]] = None
    ) -> List[str]:
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
            playlist_tracks = self.get_tracks(playlist.uri)
            playlist_value = get_playlist_value(playlist.name, mapping_value)

            nb_tracks_to_add = min(int(default_nb_songs * playlist_value), len(playlist_tracks))
            target_tracks.extend(random.sample(playlist_tracks, nb_tracks_to_add))
        return list(set(target_tracks))


#### Utilities functions

def get_playlist_value(name: str, value_mapping: Dict[str, int]) -> int:
    if value_mapping is None:
        return 1
    else:
        try:
            return value_mapping[name]
        except KeyError:
            logger.warning(f"Warning: {name} not found in the mapping given, will default to a value of 0")
            return 0
