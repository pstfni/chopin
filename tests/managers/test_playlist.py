from unittest.mock import patch

import pytest

from managers.playlist import PlaylistManager, get_playlist_value
from schemas.base import PlaylistData


@patch("managers.client.ClientManager.get_tracks")
def test_playlist_compose_standard_case(
    mock_get_tracks, playlist_1_tracks, playlist_2_tracks, playlist_1, playlist_2, mock_client_manager
):
    playlist_manager = PlaylistManager(mock_client_manager)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(playlists=[playlist_1, playlist_2], nb_songs=20)
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == len([t for t in tracks if t.id.startswith("q")]) == 10


@patch("managers.client.ClientManager.get_tracks")
def test_playlist_compose_with_mapping_value(
    mock_get_tracks, playlist_1_tracks, playlist_2_tracks, playlist_1, playlist_2, mock_client_manager
):
    playlist_manager = PlaylistManager(mock_client_manager)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(
        playlists=[playlist_1, playlist_2], nb_songs=20, mapping_value={"p": 1.5, "q": 0.5}
    )
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == 15
    assert len([t for t in tracks if t.id.startswith("q")]) == 5


@patch("managers.client.ClientManager.get_tracks")
def test_playlist_compose_with_partial_mapping_value(
    mock_get_tracks, playlist_1_tracks, playlist_2_tracks, playlist_1, playlist_2, mock_client_manager
):
    playlist_manager = PlaylistManager(mock_client_manager)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(playlists=[playlist_1, playlist_2], nb_songs=20, mapping_value={"p": 1.5})
    assert len(tracks) == 15
    assert len([t for t in tracks if t.id.startswith("p")]) == 15


@patch("managers.client.ClientManager.get_tracks")
def test_playlist_compose_with_empty_playlists(
    mock_get_tracks, playlist_1_tracks, playlist_2_tracks, mock_client_manager
):
    playlist_manager = PlaylistManager(mock_client_manager)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(playlists=[], nb_songs=20)
    assert len(tracks) == 0


# Patchs are read bottom-up by pytest 🤯
@patch("managers.client.ClientManager.get_this_is_playlist")
@patch("managers.client.ClientManager.get_tracks")
@pytest.mark.parametrize(
    "nb_tracks, this_is_side_effect, expected_nb_songs",
    [
        (10, PlaylistData(name="a", uri="uri"), 10),
        (20, PlaylistData(name="a", uri="uri"), 20),
        # No playlists found by the client: 0 tracks returned
        (10, None, 0),
    ],
)
def test_tracks_from_artist_name(
    mock_get_tracks,
    mock_get_this_is_playlist,
    playlist_1_tracks,
    nb_tracks,
    this_is_side_effect,
    expected_nb_songs,
    mock_client_manager,
):
    playlist_manager = PlaylistManager(mock_client_manager)
    mock_get_tracks.side_effect = [playlist_1_tracks]
    mock_get_this_is_playlist.side_effect = [this_is_side_effect]
    tracks = playlist_manager.tracks_from_artist_name(artist_name="Artist", nb_tracks=nb_tracks)
    assert len(tracks) == expected_nb_songs


@pytest.mark.parametrize(
    "name, mapping, expected",
    [
        # standard case
        ("playlist", {"playlist": 1}, 1),
        # multiple playlists in the mapping
        ("playlist", {"playlist": 1, "other": 2}, 1),
        # name not in the mapping
        ("playlist", {"other": 2}, 0),
        # empty mapping
        ("playlist", {}, 0),
    ],
)
def test_get_playlist_value(name, mapping, expected):
    output = get_playlist_value(name, mapping)
    assert output == expected
