from datetime import datetime
from unittest.mock import patch

import pytest

from chopin.client.playlists import create_playlist, get_playlist_tracks, get_user_playlists
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData


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


@pytest.mark.parametrize("added_at", [None, datetime(2023, 12, 12, 0, 0, 0)])
def test_get_playlist_tracks(spotify_track, added_at):
    response = {"items": [dict(added_at=added_at, track=spotify_track)]}
    with patch("chopin.client.playlists._client.playlist_items", side_effect=[response, {"items": []}]):
        playlist_tracks = get_playlist_tracks(playlist_uri="test", release_date_range=None)
    assert len(playlist_tracks) == 1
    assert isinstance(playlist_tracks[0], TrackData)
    if added_at:
        added_at = added_at.date()
    assert playlist_tracks[0].added_at == added_at


@pytest.mark.parametrize(
    "release_date_range, expected_nb_tracks",
    [
        (None, 1),
        ((datetime(2023, 12, 12).date(), datetime.now().date()), 0),
        ((datetime(1980, 1, 1).date(), datetime(1990, 1, 1).date()), 1),
    ],
)
def test_get_playlist_tracks_with_release_date_range(spotify_track, release_date_range, expected_nb_tracks):
    # hint: fixture release date is (1981, 12, 1)
    response = {"items": [dict(added_at=None, track=spotify_track)]}
    with patch("chopin.client.playlists._client.playlist_items", side_effect=[response, {"items": []}]):
        playlist_tracks = get_playlist_tracks(playlist_uri="test", release_date_range=release_date_range)
    assert len(playlist_tracks) == expected_nb_tracks
