import spotipy
from spotipy.oauth2 import SpotifyOAuth

from managers import CONFIG


class SpotifyClient:
    def __init__(self):
        auth_manager = SpotifyOAuth(
            client_id=CONFIG["client_id"],
            client_secret=CONFIG["client_secret"],
            redirect_uri="http://localhost:8888/callback",
            scope=CONFIG["scope"],
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        return self.client
