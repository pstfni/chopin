"""Genres related endpoints."""

from chopin.client.settings import _client
from chopin.constants import constants
from chopin.schemas.playlist import PlaylistData


def get_genre_mix_playlist(genre: str) -> PlaylistData | None:
    """From a given `genre`, search for a Spotify "mix" playlist and retrieve it.

    Examples:
        >>> get_genre_mix_playlist(genre="bossa nova").name
        "Bossa Nova Mix"

    Args:
        genre: A string to search for

    Returns:
        If found, the retrieved playlist.
    """
    response = _client.search(q=f"{genre} mix", limit=10, type="playlist", market="fr")["playlists"]
    items = response.get("items")
    playlist = [playlist for playlist in items if playlist["owner"]["uri"] == constants.SPOTIFY_USER_URI]
    if playlist:
        return PlaylistData(**playlist[0])
