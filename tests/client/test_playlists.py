from unittest.mock import patch

import pytest

from chopin.client.playlists import create_playlist, get_user_playlists
from chopin.schemas.playlist import PlaylistData


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
def test_get_user_playlists(user_playlists, expected_playlist_data):
    get_user_playlists.cache_clear()
    with patch("chopin.client.playlists._client.current_user_playlists", return_value=user_playlists):
        playlists = get_user_playlists()
    assert playlists == expected_playlist_data


def test_create_playlist(spotify_playlist, spotify_user):
    with patch("chopin.client.playlists._client.user_playlist_create", return_value=spotify_playlist), patch(
        "chopin.client.playlists._client.current_user", return_value=spotify_user
    ):
        playlist = create_playlist(name="string", description="string")

    assert isinstance(playlist, PlaylistData)
    # from the fixture and not the `create_playlist` method arg
    assert playlist.name == "string"
    assert playlist.uri == "string"
