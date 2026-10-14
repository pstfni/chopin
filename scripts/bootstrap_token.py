"""Obtain a long-lived Spotify refresh token for headless deployments.

Run this once on a machine with a browser. It performs the interactive authorization flow and
prints the refresh token, which can then be passed to a deployed instance through the
`refresh_token` environment variable. Spotify refresh tokens do not expire: they only become
invalid if you revoke the app's access or change your password.

Usage:
    uv run python scripts/bootstrap_token.py
"""

from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

from chopin.client.settings import get_config

if __name__ == "__main__":
    config = get_config()
    auth_manager = SpotifyOAuth(
        client_id=config.client_id.get_secret_value(),
        client_secret=config.client_secret.get_secret_value(),
        redirect_uri=config.redirect_uri,
        scope=config.scope,
        # Never reuse an existing token: we explicitly want a fresh authorization.
        cache_handler=MemoryCacheHandler(),
        open_browser=True,
    )
    token_info = auth_manager.get_access_token(check_cache=False)

    print("\n✅ Authorization successful.")
    print(f"   Granted scopes: {token_info['scope']}")
    print("\nAdd this to the deployed instance's environment (keep it secret, it grants access")
    print("to your Spotify account):\n")
    print(f"refresh_token={token_info['refresh_token']}")
