"""Tests for chopin.client.endpoints."""

from datetime import datetime
from unittest.mock import patch

import pytest

from chopin.client.endpoints import (
    _validate_single_track,
    _validate_tracks,
    add_to_queue,
    add_tracks_to_playlist,
    create_user_playlist,
    get_album_tracks,
    get_artist_top_tracks,
    get_current_user,
    get_currently_playing,
    get_likes,
    get_named_playlist,
    get_playlist_tracks,
    get_queue,
    get_top_artists,
    get_top_tracks,
    get_user_playlists,
    like_tracks,
    replace_tracks_in_playlist,
    search_artist,
)
from chopin.schemas.artist import ArtistData
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData
from chopin.schemas.user import UserData


@pytest.fixture
def almost_empty_track():
    return {"track": {}}


@pytest.fixture
def invalid_track():
    """A Spotify API track dict whose release_date=None triggers a ValidationError."""
    return {
        "track": {
            "album": {
                "album_type": "single",
                "total_tracks": 1,
                "available_markets": ["CA"],
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "album_id",
                "images": [],
                "name": "album",
                "release_date": None,
                "release_date_precision": "year",
                "type": "album",
                "uri": "spotify:album:album_id",
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "id",
                        "name": "name",
                        "type": "artist",
                        "uri": "string",
                    }
                ],
            },
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "id",
                    "name": "name",
                    "popularity": 0,
                    "type": "artist",
                    "uri": "string",
                }
            ],
            "available_markets": [],
            "disc_number": 1,
            "duration_ms": 0,
            "explicit": False,
            "external_ids": {"isrc": "string"},
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "track_id",
            "name": "track",
            "popularity": 0,
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:track_id",
            "is_local": False,
        }
    }


@pytest.fixture
def valid_track():
    """A minimal but valid Spotify API track dict."""
    return {
        "track": {
            "album": {
                "album_type": "single",
                "total_tracks": 1,
                "available_markets": ["CA"],
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "album_id",
                "images": [],
                "name": "album",
                "release_date": "1981-12",
                "release_date_precision": "year",
                "type": "album",
                "uri": "spotify:album:album_id",
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "id",
                        "name": "name",
                        "type": "artist",
                        "uri": "string",
                    }
                ],
            },
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "id",
                    "name": "name",
                    "popularity": 0,
                    "type": "artist",
                    "uri": "string",
                }
            ],
            "available_markets": [],
            "disc_number": 1,
            "duration_ms": 0,
            "explicit": False,
            "external_ids": {"isrc": "string"},
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "track_id",
            "name": "track",
            "popularity": 0,
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:track_id",
            "is_local": False,
        }
    }


@pytest.fixture
def spotify_artist():
    return {
        "external_urls": {"spotify": "string"},
        "genres": ["rock"],
        "href": "string",
        "id": "artist_id",
        "images": [],
        "name": "Test Artist",
        "popularity": 50,
        "type": "artist",
        "uri": "spotify:artist:artist_id",
    }


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("response", [None, {"currently_playing_type": "episode"}])
def test_get_currently_playing_returns_none(response):
    with patch("chopin.client.endpoints._client.current_playback", return_value=response):
        assert get_currently_playing() is None


def test_get_currently_playing_returns_track_data(spotify_track):
    response = {"currently_playing_type": "track", "item": spotify_track}
    with patch("chopin.client.endpoints._client.current_playback", return_value=response):
        assert isinstance(get_currently_playing(), TrackData)


def test_get_queue_raises_when_not_playing():
    with patch("chopin.client.endpoints._client.current_playback", return_value={}), pytest.raises(ValueError):
        get_queue()


# ---------------------------------------------------------------------------
# Artist
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "items, name, expect_result",
    [
        ([], "Test Artist", False),
        (
            [{"name": "Test Artist", "id": "id", "uri": "spotify:artist:id", "genres": []}],
            "Test Artist",
            True,
        ),
        (
            [{"name": "Other Artist", "id": "id", "uri": "spotify:artist:id", "genres": []}],
            "Test Artist",
            False,
        ),
    ],
)
def test_search_artist(items, name, expect_result):
    response = {"artists": {"items": items}}
    with patch("chopin.client.endpoints._client.search", return_value=response):
        result = search_artist(name)
    assert (result is not None) == expect_result
    if expect_result:
        assert isinstance(result, ArtistData)


def test_get_artist_top_tracks(spotify_artist, spotify_track):
    artist = ArtistData(**spotify_artist)
    with patch(
        "chopin.client.endpoints._client.artist_top_tracks",
        return_value={"tracks": [spotify_track] * 10},
    ):
        result = get_artist_top_tracks(artist, max_tracks=5)
    assert len(result) == 5
    assert all(isinstance(t, TrackData) for t in result)


# ---------------------------------------------------------------------------
# Track validation
# ---------------------------------------------------------------------------


def test_validate_single_track_no_key():
    assert _validate_single_track({}) is None


def test_validate_single_track_valid(valid_track):
    assert isinstance(_validate_single_track(valid_track), TrackData)


def test_validate_single_track_invalid_logs_warning(caplog, invalid_track):
    result = _validate_single_track(invalid_track)
    assert result is None
    assert "Error in track validation" in caplog.text


@pytest.mark.parametrize(
    "tracks, expected_count",
    [
        ([], 0),
        ([{}], 0),  # empty track wrapper
    ],
)
def test_validate_tracks(tracks, expected_count):
    assert len(_validate_tracks(tracks)) == expected_count


def test_validate_tracks_keeps_valid(valid_track):
    result = _validate_tracks([{}, valid_track])
    assert len(result) == 1
    assert isinstance(result[0], TrackData)


# ---------------------------------------------------------------------------
# User playlists
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "api_response, expected",
    [
        ({}, []),
        (
            {"items": [{"name": "p", "id": "pid", "uri": "puri"}]},
            [PlaylistData(name="p", id="pid", uri="puri")],
        ),
        (
            {"items": [{"name": "p", "id": "pid", "uri": "puri"}, {"name": "p💚", "id": "pid", "uri": "puri"}]},
            [PlaylistData(name="p", id="pid", uri="puri"), PlaylistData(name="p", id="pid", uri="puri")],
        ),
    ],
)
def test_get_user_playlists(api_response, expected):
    get_user_playlists.cache_clear()
    with patch("chopin.client.endpoints._client.current_user_playlists", return_value=api_response):
        assert get_user_playlists() == expected


@pytest.mark.parametrize("name, found", [("p", True), ("unknown", False)])
def test_get_named_playlist(name, found, playlist_1, playlist_2):
    with patch("chopin.client.endpoints.get_user_playlists", return_value=[playlist_1, playlist_2]):
        if found:
            result = get_named_playlist(name)
            assert isinstance(result, PlaylistData)
        else:
            with pytest.raises(ValueError):
                get_named_playlist(name)


# ---------------------------------------------------------------------------
# Playlist tracks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("added_at", [None, datetime(2023, 12, 12)])
def test_get_playlist_tracks(spotify_track, added_at):
    response = {"items": [{"added_at": added_at, "track": spotify_track}]}
    with patch("chopin.client.endpoints._client.playlist_items", side_effect=[response, {"items": []}]):
        result = get_playlist_tracks("playlist_id")
    assert len(result) == 1
    assert isinstance(result[0], TrackData)


@pytest.mark.parametrize(
    "release_date_range, expected_count",
    [
        (None, 1),
        ((datetime(2023, 12, 12), datetime.now()), 0),
        ((datetime(1980, 1, 1), datetime(1990, 1, 1)), 1),  # fixture release_date is 1981-12
    ],
)
def test_get_playlist_tracks_with_release_date_range(spotify_track, release_date_range, expected_count):
    response = {"items": [{"added_at": None, "track": spotify_track}]}
    with patch("chopin.client.endpoints._client.playlist_items", side_effect=[response, {"items": []}]):
        result = get_playlist_tracks("playlist_id", release_date_range=release_date_range)
    assert len(result) == expected_count


def test_create_user_playlist():
    api_response = {"name": "My Playlist", "uri": "spotify:playlist:id", "id": "id"}
    with patch("chopin.client.endpoints._client.user_playlist_create", return_value=api_response):
        result = create_user_playlist("user_id", "My Playlist")
    assert isinstance(result, PlaylistData)
    assert result.name == "My Playlist"


@pytest.mark.parametrize(
    "num_tracks, expected_calls",
    [
        (10, 1),
        (100, 2),  # paginated: 99 + 1
    ],
)
def test_add_tracks_to_playlist(num_tracks, expected_calls):
    track_ids = [f"track_{i}" for i in range(num_tracks)]
    with patch("chopin.client.endpoints._client.playlist_add_items") as mock_add:
        add_tracks_to_playlist("playlist_id", track_ids)
    assert mock_add.call_count == expected_calls


def test_replace_tracks_in_playlist(playlist_1_tracks):
    new_ids = ["new_1", "new_2"]
    with (
        patch("chopin.client.endpoints.get_playlist_tracks", return_value=playlist_1_tracks),
        patch("chopin.client.endpoints._client.playlist_remove_all_occurrences_of_items") as mock_remove,
        patch("chopin.client.endpoints._client.playlist_add_items") as mock_add,
    ):
        replace_tracks_in_playlist("playlist_id", new_ids)
    mock_remove.assert_called()
    mock_add.assert_called_with("playlist_id", new_ids)


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


def test_get_current_user(spotify_user):
    get_current_user.cache_clear()
    with patch("chopin.client.endpoints._client.current_user", return_value=spotify_user):
        result = get_current_user()
    assert isinstance(result, UserData)
    assert result.name == spotify_user["display_name"]


def test_get_likes(spotify_track):
    response = {"items": [{"track": spotify_track}]}
    with patch("chopin.client.endpoints._client.current_user_saved_tracks", return_value=response):
        result = get_likes()
    assert len(result) == 1
    assert isinstance(result[0], TrackData)


def test_add_to_queue(playlist_1_tracks):
    track = playlist_1_tracks[0]
    with patch("chopin.client.endpoints._client.add_to_queue") as mock_add:
        add_to_queue(track)
    mock_add.assert_called_once_with(track.uri)


def test_like_tracks():
    uris = ["spotify:track:1", "spotify:track:2"]
    with patch("chopin.client.endpoints._client.current_user_saved_tracks_add") as mock_like:
        like_tracks(uris)
    mock_like.assert_called_once_with(uris)


@pytest.mark.parametrize("time_range", ["short_term", "medium_term", "long_term"])
def test_get_top_tracks(time_range, spotify_track):
    with patch(
        "chopin.client.endpoints._client.current_user_top_tracks",
        return_value={"items": [spotify_track]},
    ):
        result = get_top_tracks(time_range, limit=10)
    assert len(result) == 1
    assert isinstance(result[0], TrackData)


def test_get_top_tracks_caps_limit(spotify_track):
    with patch(
        "chopin.client.endpoints._client.current_user_top_tracks",
        return_value={"items": [spotify_track]},
    ) as mock_top:
        get_top_tracks("short_term", limit=100)
    assert mock_top.call_args.kwargs["limit"] == 50


@pytest.mark.parametrize("time_range", ["short_term", "medium_term", "long_term"])
def test_get_top_artists(time_range, spotify_artist):
    with patch(
        "chopin.client.endpoints._client.current_user_top_artists",
        return_value={"items": [spotify_artist]},
    ):
        result = get_top_artists(time_range, limit=10)
    assert len(result) == 1
    assert isinstance(result[0], ArtistData)


# ---------------------------------------------------------------------------
# Albums
# ---------------------------------------------------------------------------


def test_get_album_tracks(spotify_track):
    with patch("chopin.client.endpoints._client.album_tracks", return_value={"items": [spotify_track]}):
        result = get_album_tracks("album_id")
    assert len(result) == 1
    assert isinstance(result[0], TrackData)
