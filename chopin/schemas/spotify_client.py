"""Schemas for the spotify client."""

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class SpotifyConfig(BaseSettings):
    client_id: SecretStr
    client_secret: SecretStr
    scope: str = "user-library-read"
    redirect_uri: AnyHttpUrl = "http://localhost:8888/callback"

    model_config = SettingsConfigDict(env_file=".env")
