from unittest.mock import MagicMock

import pytest

from chopin.managers.track import TrackManager
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
