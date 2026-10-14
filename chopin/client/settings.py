"""Create the spotipy auth and client."""

from functools import cache
from typing import Any

import spotipy
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from spotipy.cache_handler import CacheFileHandler, MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

from chopin.constants import constants


class SpotifyConfig(BaseSettings):
    """Spotify API settings.

    Credentials are read from the environment, or from a `.env` file. Note that the field names are
    the environment variable names: `client_id`, `client_secret`, ... (case insensitive).

    For headless deployments, set `refresh_token` so that no interactive browser authorization is
    needed. Use `scripts/bootstrap_token.py` to obtain one.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    client_id: SecretStr
    client_secret: SecretStr
    scope: str = constants.SPOTIFY_SCOPE
    redirect_uri: str = "http://localhost:8888/callback"

    requests_timeout: float = 20.0

    refresh_token: SecretStr | None = None
    cache_path: str = ".spotipy_cache"
    open_browser: bool = False


@cache
def get_config() -> SpotifyConfig:
    """Load the Spotify configuration.

    The configuration is cached, so that the environment is only read once.

    Returns:
        The Spotify settings.
    """
    return SpotifyConfig()


def _cache_handler(config: SpotifyConfig):
    """Build the spotipy cache handler holding the OAuth token.

    When a refresh token is configured, an in-memory handler is seeded with an already expired
    token. Spotipy then transparently refreshes it, which means no interactive authorization and no
    writeable filesystem are required.

    Args:
        config: The Spotify settings.

    Returns:
        A spotipy cache handler.
    """
    if config.refresh_token is None:
        return CacheFileHandler(cache_path=config.cache_path)

    token_info: dict[str, Any] = {
        "access_token": "",
        "token_type": "Bearer",
        "expires_in": 0,
        "expires_at": 0,
        "scope": config.scope,
        "refresh_token": config.refresh_token.get_secret_value(),
    }
    return MemoryCacheHandler(token_info=token_info)


@cache
def get_client() -> spotipy.Spotify:
    """Build the Spotify client.

    The client is built lazily and cached, so that importing this module never triggers an
    authorization flow.

    Returns:
        An authenticated spotipy client.
    """
    config = get_config()
    auth_manager = SpotifyOAuth(
        client_id=config.client_id.get_secret_value(),
        client_secret=config.client_secret.get_secret_value(),
        redirect_uri=config.redirect_uri,
        scope=config.scope,
        cache_handler=_cache_handler(config),
        open_browser=config.open_browser,
    )
    return spotipy.Spotify(auth_manager=auth_manager, requests_timeout=config.requests_timeout)


class _LazyClient:
    """A proxy deferring the creation of the Spotify client to its first use.

    This keeps `_client.<endpoint>(...)` call sites working while making sure that no credential is
    read, and no authorization is attempted, at import time.
    """

    def __getattr__(self, name: str) -> Any:
        """Delegate any attribute access to the underlying Spotify client."""
        return getattr(get_client(), name)


_client = _LazyClient()
