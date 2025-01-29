from unittest.mock import patch

from chopin.managers.composition import compose_playlist
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigListeningHistory
from chopin.schemas.playlist import PlaylistData


@patch("chopin.managers.playlist.get_this_is_playlist")
@patch("chopin.managers.playlist.get_playlist_tracks")
def test_playlist_compose_from_artists(
    mock_get_tracks, mock_get_this_is_playlist, playlist_1_tracks, playlist_2_tracks
):
    configuration = ComposerConfig(
        nb_songs=20,
        artists=[ComposerConfigItem(name="Artist", weight=1), ComposerConfigItem(name="Artist_2", weight=1)],
    )
    mock_get_this_is_playlist.side_effect = [
        PlaylistData(name="Artist", uri="uri", id="uri"),
        PlaylistData(name="Artist_2", uri="uri_2", id="uri_2"),
    ]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose_playlist(composition_config=configuration)
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == len([t for t in tracks if t.id.startswith("q")]) == 10


@patch("chopin.managers.playlist.get_this_is_playlist")
@patch("chopin.managers.playlist.get_playlist_tracks")
def test_playlist_compose_from_artists_with_different_weights(
    mock_get_tracks,
    mock_get_this_is_playlist,
    playlist_1_tracks,
    playlist_2_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20,
        artists=[ComposerConfigItem(name="Artist", weight=1), ComposerConfigItem(name="Artist_2", weight=0.5)],
    )
    mock_get_this_is_playlist.side_effect = [
        PlaylistData(
            name="Artist",
            uri="uri",
            id="uri",
        ),
        PlaylistData(name="Artist_2", uri="uri_2", id="uri2"),
    ]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose_playlist(composition_config=configuration)
    # 21 because of the ceil() when computing actual nb songs
    assert len(tracks) == 21
    assert len([t for t in tracks if t.id.startswith("p")]) == 14
    assert len([t for t in tracks if t.id.startswith("q")]) == 7


@patch("chopin.managers.playlist.get_playlist_tracks")
@patch("chopin.managers.composition.get_user_playlists")
def test_playlist_compose_from_playlists(
    mock_get_playlists,
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, playlists=[ComposerConfigItem(name="p", weight=1), ComposerConfigItem(name="q", weight=1)]
    )
    mock_get_playlists.return_value = [playlist_1, playlist_2]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose_playlist(composition_config=configuration)
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == len([t for t in tracks if t.id.startswith("q")]) == 10


@patch("chopin.managers.playlist.get_playlist_tracks")
@patch("chopin.managers.composition.get_user_playlists")
def test_playlist_compose_from_playlists_with_different_weights(
    mock_get_playlists,
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, playlists=[ComposerConfigItem(name="p", weight=1), ComposerConfigItem(name="q", weight=0.2)]
    )
    mock_get_playlists.return_value = [playlist_1, playlist_2]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose_playlist(composition_config=configuration)
    assert len(tracks) == 21
    assert len([t for t in tracks if t.id.startswith("p")]) == 17
    assert len([t for t in tracks if t.id.startswith("q")]) == 4


@patch("chopin.managers.composition.get_top_tracks")
def test_playlist_compose_from_history(
    mock_get_history_tracks,
    playlist_1_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, history=[ComposerConfigListeningHistory(time_range="short_term", weight=1)]
    )
    mock_get_history_tracks.side_effect = [playlist_1_tracks]

    tracks = compose_playlist(composition_config=configuration)
    assert mock_get_history_tracks.call_args[1]["limit"] == 20
    assert all([t.id.startswith("p") for t in tracks])


def test_playlist_compose_with_empty_playlists():
    configuration = ComposerConfig(nb_songs=20, playlists=[])
    tracks = compose_playlist(configuration)
    assert len(tracks) == 0
