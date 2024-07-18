from datetime import date

import pytest

from chopin.managers.selection import (
    SELECTION_MAPPER,
    SelectionMethod,
    _select_latest_tracks,
    _select_original_tracks,
    _select_popular_tracks,
)


def test__select_random_tracks():
    pass  # It is a numpy random choice call.


def test__select_popular_tracks(playlist_1_tracks):
    # arrange: take 3 tracks and set higher popularity values
    tracks = playlist_1_tracks
    tracks[10].popularity = 80
    tracks[25].popularity = 99
    tracks[30].popularity = 60

    selection = _select_popular_tracks(tracks, nb_tracks=3)

    assert len(selection) == 3
    assert selection[0].id == "p_25"
    assert selection[1].id == "p_10"
    assert selection[2].id == "p_30"


def test__select_popular_tracks_empty_list():
    selection = _select_popular_tracks([], nb_tracks=10)
    assert selection == []


def test__select_popular_tracks_larger_than_list(playlist_1_tracks):
    # arrange: take 3 tracks and set higher popularity values
    tracks = playlist_1_tracks
    tracks[10].popularity = 80
    tracks[25].popularity = 99
    tracks[30].popularity = 60

    selection = _select_popular_tracks(tracks, nb_tracks=1000)

    assert len(selection) == len(playlist_1_tracks)
    assert selection[0].id == "p_25"


def test__select_popular_tracks_larger_than_list_zero_tracks(playlist_1_tracks):
    selection = _select_popular_tracks(playlist_1_tracks, nb_tracks=0)
    assert selection == []


def test__select_latest_tracks(playlist_1_tracks):
    # arrange: take 3 tracks and set more recent release dates
    tracks = playlist_1_tracks
    tracks[10].album.release_date = date(year=1990, month=1, day=1)
    tracks[25].album.release_date = date(year=2024, month=1, day=1)
    tracks[30].album.release_date = date(year=1972, month=1, day=1)

    selection = _select_latest_tracks(tracks, nb_tracks=3)

    assert len(selection) == 3
    assert selection[0].id == "p_25"
    assert selection[1].id == "p_10"
    assert selection[2].id == "p_30"


def test__select_latest_tracks_empty_list():
    selection = _select_latest_tracks([], nb_tracks=10)
    assert selection == []


def test__select_latest_tracks_larger_than_list(playlist_1_tracks):
    # arrange: take 3 tracks and set more recent release dates
    tracks = playlist_1_tracks
    tracks[10].album.release_date = date(year=1990, month=1, day=1)
    tracks[25].album.release_date = date(year=2024, month=1, day=1)
    tracks[30].album.release_date = date(year=1972, month=1, day=1)

    selection = _select_latest_tracks(tracks, nb_tracks=1000)

    assert len(selection) == len(playlist_1_tracks)
    assert selection[0].id == "p_25"


def test__select_latest_tracks_larger_than_list_zero_tracks(playlist_1_tracks):
    selection = _select_latest_tracks(playlist_1_tracks, nb_tracks=0)
    assert selection == []


@pytest.mark.parametrize("nb_tracks", [0, 3, 1000])
def test__select_original_tracks(playlist_1_tracks, nb_tracks):
    # arrange: take 3 tracks and set higher popularity values
    tracks = playlist_1_tracks

    selection = _select_original_tracks(tracks, nb_tracks=nb_tracks)
    expected_nb_tracks = min(nb_tracks, len(tracks))
    assert selection[:expected_nb_tracks] == playlist_1_tracks[:expected_nb_tracks]


def test__select_original_tracks_empty_list():
    selection = _select_original_tracks([], nb_tracks=10)
    assert selection == []


def test_all_methods_are_mapped():
    assert list(SELECTION_MAPPER.keys()) == SelectionMethod._member_names_
