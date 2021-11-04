from typing import Any, Dict, List

import spotipy

from utils import get_logger
from schemas import PlaylistData

logger = get_logger(__name__)


class Playlist:
    def __init__(self, spotify_client: spotipy.Spotify, playlist_data: PlaylistData):
        self.client = spotify_client
        self.playlist = playlist_data

    def get_tracks(self) -> List[str]:
        offset: int = 0
        tracks: List[str] = []
        response: Dict[str, Any] = {'response': []}

        while response:
            response = self.client.playlist_items(self.playlist.uri,
                                                  offset=offset,
                                                  fields='items.track.id,total',
                                                  additional_types=['track'])
            offset += len(response['items'])
            response_tracks = [r['track']['id'] for r in response['items']]
            tracks.extend(response_tracks)

            if len(response['items']) == 0:
                break
        return tracks

    def fill(self, playlist_tracks: List[str]):
        paginated_tracks = [playlist_tracks[i:i + 99] for i in range(0, len(playlist_tracks), 99)]
        for page_tracks in paginated_tracks:
            self.client.playlist_add_items(self.playlist.uri, page_tracks)
