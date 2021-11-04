import spotipy
from spotipy.oauth2 import SpotifyOAuth

from models import config


class SpotifyClient():
    def __init__(self):
        auth_manager = SpotifyOAuth(client_id=config.client_id,
                                    client_secret=config.client_secret,
                                    redirect_uri="http://example.com",
                                    scope=config.scope)
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        return self.client
