from unittest.mock import patch

from models.playlist import PlaylistManager


@patch("models.playlist.PlaylistManager.get_tracks")
def test_playlist_compose_standard_case(mock_get_tracks, playlist_1_tracks, playlist_2_tracks, playlist_1, playlist_2):
    playlist_manager = PlaylistManager(None)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(playlists=[playlist_1, playlist_2], nb_songs=20)
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == len([t for t in tracks if t.id.startswith("q")]) == 10


@patch("models.playlist.PlaylistManager.get_tracks")
def test_playlist_compose_with_mapping_value(
    mock_get_tracks, playlist_1_tracks, playlist_2_tracks, playlist_1, playlist_2
):
    playlist_manager = PlaylistManager(None)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(
        playlists=[playlist_1, playlist_2], nb_songs=20, mapping_value={"p": 1.5, "q": 0.5}
    )
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == 15
    assert len([t for t in tracks if t.id.startswith("q")]) == 5


@patch("models.playlist.PlaylistManager.get_tracks")
def test_playlist_compose_with_empty_playlists(mock_get_tracks, playlist_1_tracks, playlist_2_tracks):
    playlist_manager = PlaylistManager(None)
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = playlist_manager.compose(playlists=[], nb_songs=20)
    assert len(tracks) == 0
