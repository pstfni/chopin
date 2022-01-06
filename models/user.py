from typing import Dict, List

import spotipy

from schemas import PlaylistData, UserData
from utils import get_logger, simplify_string

logger = get_logger(__name__)


class User:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client
        user = spotify_client.current_user()
        self.user = UserData(name=user["display_name"], id=user["id"], uri=user["uri"])
        self.value_mapping = None

    def create_playlist(self, name: str, description: str = "Randomly generated playlist"):
        playlist = self.client.user_playlist_create(user=self.user.id, name=name, description=description)
        return PlaylistData(name=playlist["name"], uri=playlist["uri"])

    def get_user_playlists(self) -> List[PlaylistData]:
        playlists = self.client.current_user_playlists()["items"]
        return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]

    def get_current_user(self) -> UserData:
        return self.user

    def feed_mapping_values(self, mapping_value_dict: Dict[str, int]):
        self.value_mapping = mapping_value_dict
