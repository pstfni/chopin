from unittest.mock import patch

from chopin.client.genres import get_genre_mix_playlist
from chopin.constants import constants
from chopin.schemas.playlist import PlaylistData


def test_get_genre_mix_playlist(spotify_playlist):
    spotify_playlist["owner"]["uri"] = constants.SPOTIFY_USER_URI
    search_result = {"playlists": {"items": [spotify_playlist]}}
    with patch("chopin.client.genres._client.search", return_value=search_result) as mock_search:
        playlist = get_genre_mix_playlist("genre")
    assert isinstance(playlist, PlaylistData)
    mock_search.assert_called_once_with(q="genre mix", limit=10, type="playlist", market=constants.MARKET)
