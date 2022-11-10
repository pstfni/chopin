from typing import Dict, List

import requests
import spotipy

from schemas import ArtistData, PlaylistData, TrackData, UserData
from utils import get_logger, simplify_string

logger = get_logger(__name__)


class UserManager:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client
        user = spotify_client.current_user()
        self.user = UserData(name=user["display_name"], id=user["id"], uri=user["uri"])
        self.value_mapping = None
        self._session = requests.Session()

    def create_playlist(self, name: str, description: str = "Randomly generated playlist"):
        playlist = self.client.user_playlist_create(user=self.user.id, name=name, description=description)
        return PlaylistData(name=playlist["name"], uri=playlist["uri"])

    def get_user_playlists(self) -> List[PlaylistData]:
        playlists = self.client.current_user_playlists().get("items", [])
        return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]

    def get_current_user(self) -> UserData:
        return self.user

    def get_hot_artists(self, limit=50) -> List[ArtistData]:
        response = self.client.current_user_top_artists(limit=limit, time_range="short_term")["items"]
        return [ArtistData(**artist) for artist in response]

    def get_hot_tracks(self, limit=50) -> List[TrackData]:
        response = self.client.current_user_top_tracks(limit=limit, time_range="short_term")["items"]
        return [TrackData(**track) for track in response]

    def get_top_artists(self, limit=50) -> List[ArtistData]:
        response = self.client.current_user_top_artists(limit=limit, time_range="long_term")["items"]
        return [ArtistData(**artist) for artist in response]

    def get_top_tracks(self, limit=50) -> List[TrackData]:
        response = self.client.current_user_top_tracks(limit=limit, time_range="long_term")["items"]
        return [TrackData(**track) for track in response]

    def get_queue(self) -> List[TrackData]:
        if not self.client.current_playback().get("is_playing"):
            raise ValueError(
                "Spotify should be active on a device and the playback should be on for the get_queueendpoint to work."
            )
        # unfortunately this has to be custom made ... Just a hack for now while waiting for spotipy implementation
        # TODO: check if spotify has fixed their permission issue
        headers = {
            "Authorization": f"Bearer {self.client.auth_manager.get_access_token(as_dict=False)}",
            "Content-Type": "application/json",
        }
        route = "https://api.spotify.com/v1/me/player/queue"
        try:
            response = self._session.request(
                method="GET",
                url=route,
                headers=headers,
                timeout=5,
                proxies=None,
            )
            response.raise_for_status()
            results = response.json()
        except requests.exceptions.HTTPError as http_error:
            error_response = http_error.response
            raise spotipy.SpotifyException(
                error_response.status_code, -1, f"{route}\n{error_response}", headers=error_response.headers
            )
        except ValueError:
            results = None
        return [TrackData(**track) for track in results.get("queue")]

    def get_likes(self) -> List[TrackData]:
        offset = 0
        tracks = []
        while True:
            response = self.client.current_user_saved_tracks(limit=20, offset=offset)
            tracks.extend(response.get("items"))
            offset += 20
            if not response.get("next"):
                break
        return [TrackData(**track["track"]) for track in tracks]

    def feed_mapping_values(self, mapping_value_dict: Dict[str, int]):
        self.value_mapping = mapping_value_dict
