from pathlib import Path

import dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyClient:
    def __init__(self, env_path: Path = ".env"):
        CONFIG = dotenv.dotenv_values(env_path)
        auth_manager = SpotifyOAuth(
            client_id=CONFIG["client_id"],
            client_secret=CONFIG["client_secret"],
            redirect_uri=CONFIG["redirect_uri"],
            scope=CONFIG["scope"],
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        return self.client
