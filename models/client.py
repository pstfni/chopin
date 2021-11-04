import spotipy
from spotipy.oauth2 import SpotifyOAuth

from models import CONFIG


class SpotifyClient:
    def __init__(self):
        auth_manager = SpotifyOAuth(client_id=CONFIG.get("client_id"),
                                    client_secret=CONFIG.get("client_secret"),
                                    redirect_uri="http://example.com",
                                    scope=CONFIG.get("scope"))
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        return self.client
