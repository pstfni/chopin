from typing import Dict, List

import spotipy

from schemas import PlaylistData, UserData
from utils import get_logger, simplify_string

logger = get_logger(__name__)


class Tracks:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client

    def get_user_playlists(self) -> List[PlaylistData]:
        playlists = self.client.current_user_playlists()["items"]
        return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]

    def get_current_user(self) -> UserData:
        return self.user

    def feed_mapping_values(self, mapping_value_dict: Dict[str, int]):
        self.value_mapping = mapping_value_dict
