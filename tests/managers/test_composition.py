from unittest.mock import patch

import pytest

from chopin.managers.composition import _expand_pattern_playlists, compose_playlist
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigListeningHistory
from chopin.schemas.playlist import PlaylistData


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


# --- Pattern expansion ---


@pytest.fixture
def user_playlists():
    return [
        PlaylistData(name="rock80s", id="id_rock80s", uri="spotify:playlist:id_rock80s"),
        PlaylistData(name="rock90s", id="id_rock90s", uri="spotify:playlist:id_rock90s"),
        PlaylistData(name="chill", id="id_chill", uri="spotify:playlist:id_chill"),
    ]


def test_expand_wildcard_matches_all(user_playlists):
    item = ComposerConfigItem(name="*", weight=1, nb_songs=30, selection_method="random")
    result = _expand_pattern_playlists([item], user_playlists)
    assert len(result) == 3
    assert {r.name for r in result} == {"rock80s", "rock90s", "chill"}


def test_expand_prefix_pattern_matches_subset(user_playlists):
    item = ComposerConfigItem(name="rock*", weight=2, nb_songs=20, selection_method="latest")
    result = _expand_pattern_playlists([item], user_playlists)
    assert len(result) == 2
    assert all(r.name.startswith("rock") for r in result)
    assert all(r.weight == 2 for r in result)
    assert all(r.selection_method.value == "latest" for r in result)


def test_expand_pattern_splits_nb_songs_evenly(user_playlists):
    item = ComposerConfigItem(name="rock*", weight=1, nb_songs=20, selection_method="random")
    result = _expand_pattern_playlists([item], user_playlists)
    assert all(r.nb_songs == 10 for r in result)


def test_expand_unmatched_pattern_is_skipped(user_playlists):
    item = ComposerConfigItem(name="jazz*", weight=1, nb_songs=10, selection_method="random")
    result = _expand_pattern_playlists([item], user_playlists)
    assert result == []


def test_expand_non_pattern_item_is_unchanged(user_playlists):
    item = ComposerConfigItem(name="chill", weight=1, nb_songs=10, selection_method="random")
    result = _expand_pattern_playlists([item], user_playlists)
    assert result == [item]


@patch("chopin.managers.playlist.get_playlist_tracks")
@patch("chopin.managers.composition.get_user_playlists")
def test_compose_with_wildcard_pattern(
    mock_get_playlists,
    mock_get_tracks,
    playlist_1,
    playlist_2,
    playlist_1_tracks,
    playlist_2_tracks,
):
    """A single '*' entry in the config should pull from all available playlists."""
    configuration = ComposerConfig(nb_songs=20, playlists=[ComposerConfigItem(name="*", weight=1)])
    mock_get_playlists.return_value = [playlist_1, playlist_2]
    mock_get_tracks.side_effect = [playlist_1_tracks, playlist_2_tracks]

    tracks = compose_playlist(composition_config=configuration)
    assert mock_get_tracks.call_count == 2
    assert len(tracks) == 20
