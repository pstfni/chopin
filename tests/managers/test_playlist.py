from unittest.mock import patch

import pytest

from chopin.managers.playlist import compose, create, dump, tracks_from_artist_name, tracks_from_playlist_name
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigListeningHistory
from chopin.schemas.playlist import PlaylistData, PlaylistSummary


@patch("chopin.managers.playlist.get_user_playlists")
@patch("chopin.managers.playlist.create_playlist")
@patch("chopin.managers.playlist.replace_tracks_in_playlist")
@pytest.mark.parametrize("name", ["new_playlist", "playlist_1"])
def test_create(mock_replace_tracks_in_playlist, mock_create_playlist, mock_get_user_playlists, name):
    mock_get_user_playlists.return_value = [
        PlaylistData(name="playlist_1", uri="uri"),
    ]
    mock_create_playlist.return_value = PlaylistData(name=name, uri="uri")
    mock_replace_tracks_in_playlist.return_value = 200

    playlist = create(name, "a description", overwrite=True)
    if name == "playlist_1":
        mock_replace_tracks_in_playlist.assert_called_once()
    assert playlist.name == name


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
        PlaylistData(name="Artist", uri="uri"),
        PlaylistData(name="Artist_2", uri="uri_2"),
    ]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose(composition_config=configuration)
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
        PlaylistData(name="Artist", uri="uri"),
        PlaylistData(name="Artist_2", uri="uri_2"),
    ]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose(composition_config=configuration)
    # 21 because of the ceil() when computing actual nb songs
    assert len(tracks) == 21
    assert len([t for t in tracks if t.id.startswith("p")]) == 14
    assert len([t for t in tracks if t.id.startswith("q")]) == 7


@patch("chopin.managers.playlist.get_playlist_tracks")
def test_playlist_compose_from_playlists(
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, playlists=[ComposerConfigItem(name="p", weight=1), ComposerConfigItem(name="q", weight=1)]
    )
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose(composition_config=configuration, user_playlists=[playlist_1, playlist_2])
    assert len(tracks) == 20
    assert len([t for t in tracks if t.id.startswith("p")]) == len([t for t in tracks if t.id.startswith("q")]) == 10


@patch("chopin.managers.playlist.get_playlist_tracks")
def test_playlist_compose_from_playlists_with_different_weights(
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, playlists=[ComposerConfigItem(name="p", weight=1), ComposerConfigItem(name="q", weight=0.2)]
    )
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose(composition_config=configuration, user_playlists=[playlist_1, playlist_2])
    assert len(tracks) == 21
    assert len([t for t in tracks if t.id.startswith("p")]) == 17
    assert len([t for t in tracks if t.id.startswith("q")]) == 4


@patch("chopin.managers.playlist.get_top_tracks")
def test_playlist_compose_from_history(
    mock_get_history_tracks,
    playlist_1_tracks,
):
    configuration = ComposerConfig(
        nb_songs=20, history=[ComposerConfigListeningHistory(time_range="short_term", weight=1)]
    )
    mock_get_history_tracks.side_effect = [playlist_1_tracks]

    tracks = compose(composition_config=configuration)
    assert mock_get_history_tracks.call_args[1]["limit"] == 20
    assert all([t.id.startswith("p") for t in tracks])


def test_playlist_compose_with_empty_playlists():
    configuration = ComposerConfig(nb_songs=20, playlists=[])
    tracks = compose(configuration)
    assert len(tracks) == 0


# Patchs are read bottom-up by pytest 🤯
@patch("chopin.managers.playlist.get_this_is_playlist")
@patch("chopin.managers.playlist.get_playlist_tracks")
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
):
    mock_get_tracks.side_effect = [playlist_1_tracks]
    mock_get_this_is_playlist.side_effect = [this_is_side_effect]
    tracks = tracks_from_artist_name(artist_name="Artist", nb_tracks=nb_tracks)
    assert len(tracks) == expected_nb_songs


@patch("chopin.managers.playlist.get_playlist_tracks")
def test_tracks_from_playlist_name(
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
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
