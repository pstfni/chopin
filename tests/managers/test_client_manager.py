from unittest.mock import MagicMock

import pytest
from spotipy.client import Spotify

from chopin.managers.client import ClientManager
from chopin.schemas.base import PlaylistData


def test_create_playlist(spotify_playlist, spotify_user, mock_client_manager):
    mock_client = Spotify()
    mock_client.current_user = MagicMock(return_value=spotify_user)
    mock_client.user_playlist_create = MagicMock(return_value=spotify_playlist)
    user_manager = ClientManager(mock_client)

    playlist = user_manager.create_playlist(name="", description="")
    assert isinstance(playlist, PlaylistData)
    # from the fixture and not the `create_playlist` method arg
    assert playlist.name == "string"
    assert playlist.uri == "string"


@pytest.mark.parametrize(
    "user_playlists, expected_playlist_data",
    [
        # empty playlists
        ({}, []),
        # standard name
        ({"items": [{"name": "p", "id": "pid", "uri": "puri"}]}, [PlaylistData(name="p", id="pid", uri="puri")]),
        # several playlists, incl. emojis in their names.
        (
            {"items": [{"name": "p", "id": "pid", "uri": "puri"}, {"name": "p💚", "id": "pid", "uri": "puri"}]},
            [PlaylistData(name="p", id="pid", uri="puri"), PlaylistData(name="p", id="pid", uri="puri")],
        ),
    ],
)
def test_get_user_playlists(spotify_user, user_playlists, expected_playlist_data):
    mock_client = Spotify()
    mock_client.current_user = MagicMock(return_value=spotify_user)
    mock_client.current_user_playlists = MagicMock(return_value=user_playlists)
    user_manager = ClientManager(mock_client)

    playlists = user_manager.get_user_playlists()
    assert playlists == expected_playlist_data
