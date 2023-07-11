"""Spotipy client initialization."""
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from chopin.schemas.spotify_client import SpotifyConfig


class SpotifyClient:
    """Spotify client (via the spotipy lib) used in the app."""

    def __init__(self):
        config = SpotifyConfig()
        auth_manager = SpotifyOAuth(
            client_id=config.client_id.get_secret_value(),
            client_secret=config.client_secret.get_secret_value(),
            redirect_uri=config.redirect_uri,
            scope=config.scope,
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)

    def get_client(self) -> spotipy.Spotify:
        """Get spotify client."""
        return self.client
