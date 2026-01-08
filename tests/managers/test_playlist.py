from unittest.mock import patch

import pytest

from chopin.managers.playlist import create, create_playlist, doppelganger_playlist, dump, tracks_from_playlist_name
from chopin.schemas.playlist import PlaylistData, PlaylistSummary


@patch("chopin.managers.playlist.get_user_playlists")
@patch("chopin.managers.playlist.create_playlist")
@patch("chopin.managers.playlist.replace_tracks_in_playlist")
@pytest.mark.parametrize("name", ["new_playlist", "playlist_1"])
def test_create(mock_replace_tracks_in_playlist, mock_create_playlist, mock_get_user_playlists, name):
    mock_get_user_playlists.return_value = [
        PlaylistData(name="playlist_1", uri="uri", id="uri"),
    ]
    mock_create_playlist.return_value = PlaylistData(name=name, uri="uri", id="uri")
    mock_replace_tracks_in_playlist.return_value = 200

    playlist = create(name, "a description", overwrite=True)
    if name == "playlist_1":
        mock_replace_tracks_in_playlist.assert_called_once()
    assert playlist.name == name


@patch("chopin.managers.playlist.get_playlist_tracks")
def test_tracks_from_playlist_name(
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
):
    mock_get_tracks.side_effect = [playlist_1_tracks]
    tracks = tracks_from_playlist_name(playlist_name="p", nb_tracks=10, user_playlists=[playlist_1, playlist_2])

    assert len(tracks) == 10
    assert all(t.name.startswith("test_track_p") for t in tracks)


def test_dump(tmp_path, playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    outfile = tmp_path / "outfile.json"
    with open(outfile, "w"):
        dump(playlist_summary, outfile)
    assert outfile.exists()


def test_create_playlist(spotify_playlist, spotify_user):
    with (
        patch("chopin.client.endpoints._client.user_playlist_create", return_value=spotify_playlist),
        patch("chopin.client.endpoints._client.current_user", return_value=spotify_user),
    ):
        playlist = create_playlist(name="string", description="string")

    assert isinstance(playlist, PlaylistData)
    # from the fixture and not the `create_playlist` method arg
    assert playlist.name == "string"
    assert playlist.uri == "string"


@patch("chopin.managers.playlist.get_named_playlist")
@patch("chopin.managers.playlist.get_playlist_tracks")
@patch("chopin.managers.playlist.get_album_tracks")
@patch("chopin.managers.playlist.create")
@patch("chopin.managers.playlist.fill")
def test_doppelganger_playlist(
    mock_fill,
    mock_create,
    mock_get_album_tracks,
    mock_get_playlist_tracks,
    mock_get_named_playlist,
    playlist_1,
    playlist_1_tracks,
    album_tracks,
):
    mock_get_named_playlist.return_value = playlist_1
    mock_get_playlist_tracks.return_value = playlist_1_tracks
    mock_get_album_tracks.return_value = album_tracks

    created_playlist = doppelganger_playlist(source_playlist="Playlist 1", new_playlist="Playlist 2")

    mock_get_named_playlist.assert_called_once_with("Playlist 1")
    mock_get_playlist_tracks.assert_called_once_with(playlist_1.id)
    mock_create.assert_called_once_with("Playlist 2", overwrite=True)
    mock_fill.assert_called_once()

    filled_tracks = mock_fill.call_args[1]["tracks"]
    assert len(filled_tracks) == len(playlist_1_tracks)


@patch("chopin.managers.playlist.get_named_playlist")
@patch("chopin.managers.playlist.get_playlist_tracks")
@patch("chopin.managers.playlist.create")
def test_doppelganger_playlist_empty(mock_create, mock_get_playlist_tracks, mock_get_named_playlist, playlist_1):
    # Arrange
    mock_get_named_playlist.return_value = playlist_1
    mock_get_playlist_tracks.return_value = []

    # Act
    doppelganger_playlist(source_playlist="Playlist 1", new_playlist="Playlist 2")

    # Assert
    mock_get_named_playlist.assert_called_once_with("Playlist 1")
    mock_get_playlist_tracks.assert_called_once_with(playlist_1.id)
    mock_create.assert_not_called()
