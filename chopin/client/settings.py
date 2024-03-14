"""Configuration for the Spotify 'Spotipy' client."""

import spotipy
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from spotipy.oauth2 import SpotifyOAuth


class SpotifyConfig(BaseSettings):
    """Spotify API settings."""

    model_config = SettingsConfigDict(env_file=".env")

    client_id: SecretStr
    client_secret: SecretStr
    scope: str = "user-library-read"
    redirect_uri: str = "http://localhost:8888/callback"

    requests_timeout: float = 20.0


class Settings(BaseSettings):
    """Valohai library settings pydantic model."""

    config: SpotifyConfig = SpotifyConfig()
    client: spotipy.Spotify = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config.client_id.get_secret_value(),
            client_secret=config.client_secret.get_secret_value(),
            redirect_uri=config.redirect_uri,
            scope=config.scope,
        )
    )


settings = Settings()
_client = settings.client
