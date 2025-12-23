from datetime import datetime
from unittest.mock import patch

import pytest

from chopin.client.endpoints import _validate_tracks, get_playlist_tracks, get_user_playlists
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData


@pytest.fixture
def almost_empty_track():
    return {"track": {}}


@pytest.fixture
def invalid_track():
    return {
        "track": {
            "album": {
                "album_type": "compilation",
                "total_tracks": 9,
                "available_markets": ["CA", "BR", "IT"],
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "2up3OPMp9Tb4dAKM2erWXQ",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                        "height": 300,
                        "width": 300,
                    }
                ],
                "name": "string",
                "release_date": None,
                "release_date_precision": "year",
                "restrictions": {"reason": "market"},
                "type": "album",
                "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
                "album_group": "compilation",
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "string",
                        "name": "string",
                        "type": "artist",
                        "uri": "string",
                    }
                ],
            },
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "followers": {"href": "string", "total": 0},
                    "genres": ["Prog rock", "Grunge"],
                    "href": "string",
                    "id": "string",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                            "height": 300,
                            "width": 300,
                        }
                    ],
                    "name": "string",
                    "popularity": 0,
                    "type": "artist",
                    "uri": "string",
                }
            ],
            "available_markets": ["string"],
            "disc_number": 0,
            "duration_ms": 0,
            "explicit": True,
            "external_ids": {"isrc": "string", "ean": "string", "upc": "string"},
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "string",
            "is_playable": True,
            "restrictions": {"reason": "string"},
            "name": "string",
            "popularity": 0,
            "preview_url": "string",
            "track_number": 0,
            "type": "string",
            "uri": "string",
            "is_local": True,
        }
    }


@pytest.fixture
def valid_track():
    return {
        "track": {
            "album": {
                "album_type": "compilation",
                "total_tracks": 9,
                "available_markets": ["CA", "BR", "IT"],
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "2up3OPMp9Tb4dAKM2erWXQ",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                        "height": 300,
                        "width": 300,
                    }
                ],
                "name": "string",
                "release_date": "1981-12",
                "release_date_precision": "year",
                "restrictions": {"reason": "market"},
                "type": "album",
                "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
                "album_group": "compilation",
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "string",
                        "name": "string",
                        "type": "artist",
                        "uri": "string",
                    }
                ],
            },
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "followers": {"href": "string", "total": 0},
                    "genres": ["Prog rock", "Grunge"],
                    "href": "string",
                    "id": "string",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                            "height": 300,
                            "width": 300,
                        }
                    ],
                    "name": "string",
                    "popularity": 0,
                    "type": "artist",
                    "uri": "string",
                }
            ],
            "available_markets": ["string"],
            "disc_number": 0,
            "duration_ms": 0,
            "explicit": True,
            "external_ids": {"isrc": "string", "ean": "string", "upc": "string"},
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "string",
            "is_playable": True,
            "restrictions": {"reason": "string"},
            "name": "string",
            "popularity": 0,
            "preview_url": "string",
            "track_number": 0,
            "type": "string",
            "uri": "string",
            "is_local": True,
        }
    }


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
    with patch("chopin.client.endpoints._client.current_user_playlists", return_value=user_playlists):
        playlists = get_user_playlists()
    assert playlists == expected_playlist_data


@pytest.mark.parametrize("added_at", [None, datetime(2023, 12, 12, 0, 0, 0)])
def test_get_playlist_tracks(spotify_track, added_at):
    response = {"items": [dict(added_at=added_at, track=spotify_track)]}
    with patch("chopin.client.endpoints._client.playlist_items", side_effect=[response, {"items": []}]):
        playlist_tracks = get_playlist_tracks(playlist_id="test", release_date_range=None)
    assert len(playlist_tracks) == 1
    assert isinstance(playlist_tracks[0], TrackData)
    if added_at:
        added_at = added_at.date()
    assert playlist_tracks[0].added_at == added_at


@pytest.mark.parametrize(
    "release_date_range, expected_nb_tracks",
    [
        (None, 1),
        ((datetime(2023, 12, 12), datetime.now()), 0),
        ((datetime(1980, 1, 1), datetime(1990, 1, 1)), 1),
    ],
)
def test_get_playlist_tracks_with_release_date_range(spotify_track, release_date_range, expected_nb_tracks):
    # hint: fixture release date is (1981, 12, 1)
    response = {"items": [dict(added_at=None, track=spotify_track)]}
    with patch("chopin.client.endpoints._client.playlist_items", side_effect=[response, {"items": []}]):
        playlist_tracks = get_playlist_tracks(playlist_id="test", release_date_range=release_date_range)
    assert len(playlist_tracks) == expected_nb_tracks


def test_validation_one_empty_track(valid_track):
    in_tracks = [{}, valid_track]
    tracks = _validate_tracks(in_tracks)
    assert len(tracks) == 1


def test_validation_almost_empty_track(almost_empty_track):
    in_tracks = [almost_empty_track]
    tracks = _validate_tracks(in_tracks)
    assert tracks == []


def test_validation_invalid_track(caplog, invalid_track):
    in_tracks = [invalid_track]
    tracks = _validate_tracks(in_tracks)
    assert tracks == []
    assert "Error in track validation" in caplog.text
