import random
from unittest.mock import MagicMock

import pytest

from chopin.managers.track import TrackManager, find_seeds, shuffle_tracks
from chopin.schemas.base import TrackData, TrackFeaturesData
from tests.conftest import spotify_audio_feature


def side_effect_audio_features(tracks):
    return [spotify_audio_feature() for _ in range(len(tracks))]


@pytest.mark.parametrize("track_list", ["playlist_1_tracks", "playlist_2_tracks", "empty_playlist"])
def test_get_audio_features(track_list, request, mock_client_manager):
    track_list = request.getfixturevalue(track_list)
    track_manager = TrackManager(mock_client_manager)
    mock_client_manager.get_tracks_audio_features = MagicMock(side_effect=side_effect_audio_features)

    audio_features = track_manager.get_audio_features(track_list)
    assert len(audio_features) == len(track_list)


@pytest.mark.parametrize("track_list", ["playlist_1_tracks", "playlist_2_tracks", "empty_playlist"])
def test_set_audio_features(track_list, request, mock_client_manager):
    track_list = request.getfixturevalue(track_list)
    track_manager = TrackManager(mock_client_manager)
    mock_client_manager.get_tracks_audio_features = MagicMock(side_effect=side_effect_audio_features)

    tracks_with_audio_features = track_manager.set_audio_features(track_list)
    assert len(tracks_with_audio_features) == len(track_list)
    for track in tracks_with_audio_features:
        assert track.features is not None


@pytest.mark.parametrize(
    "feature, value, expected_track_id",
    [
        # high acousticness
        ("acousticness", 0.82, "chill_track"),
        # high energy
        ("energy", 0.6, "pop_track"),
        # low instrumentalness
        ("instrumentalness", 0.02, "pop_track"),
        # unknown feature
        pytest.param("valence", 0.82, 0, marks=pytest.mark.xfail(strict=True, raises=ValueError)),
    ],
)
def test_find_seeds(feature, value, expected_track_id, mock_client_manager):
    # Arrange
    track_1 = TrackData(
        name="chill track",
        id="chill_track",
        uri="",
        duration_ms=0,
        popularity=0,
        features=TrackFeaturesData(
            acousticness=0.8,
            instrumentalness=0.6,
            danceability=0.2,
            energy=0.2,
        ),
    )
    track_2 = TrackData(
        name="pop track",
        id="pop_track",
        uri="",
        duration_ms=0,
        popularity=0,
        features=TrackFeaturesData(
            acousticness=0.2,
            instrumentalness=0.3,
            danceability=0.8,
            energy=0.7,
        ),
    )
    tracks = [track_1, track_2]

    out_track = find_seeds(tracks, feature, value, nb_seeds=1)
    assert out_track[0].id == expected_track_id


def test_shuffle_tracks(playlist_1_tracks):
    random.seed(42)
    tracks = shuffle_tracks(playlist_1_tracks)
    assert len(tracks) == len(playlist_1_tracks)
    assert tracks[0].name == "test_track_p_40"
