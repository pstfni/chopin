import spotipy
from spotipy.oauth2 import SpotifyOAuth

from models import CONFIG


class SpotifyClient:
    def __init__(self):
        auth_manager = SpotifyOAuth(
            client_id=CONFIG["client_id"],
            client_secret=CONFIG["client_secret"],
            redirect_uri="http://example.com",
            scope=CONFIG["scope"],
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        print(self.client.auth_manager._redirect_uri)
        return self.client
