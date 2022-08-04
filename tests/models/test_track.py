from unittest.mock import MagicMock

import pytest
from spotipy.client import Spotify

from models.track import TrackManager
from schemas import TrackData, TrackFeaturesData
from tests.conftest import audio_feature


def side_effect_audio_features(tracks):
    return [audio_feature for _ in range(len(tracks))]


@pytest.mark.parametrize("nb_tracks", [0, 4, 120])
def test_get_audio_features(nb_tracks):
    mock_client = Spotify()
    mock_client.audio_features = MagicMock(side_effect=side_effect_audio_features)
    track_manager = TrackManager(mock_client)

    audio_features = track_manager.get_audio_features(uris=[str(i) for i in range(nb_tracks)])
    assert len(audio_features) == nb_tracks


@pytest.mark.parametrize("track_list", ["playlist_1_tracks", "playlist_2_tracks", "empty_playlist"])
def test_set_audio_features(track_list, request):
    track_list = request.getfixturevalue(track_list)
    mock_client = Spotify()
    mock_client.audio_features = MagicMock(side_effect=side_effect_audio_features)
    track_manager = TrackManager(mock_client)

    tracks_with_audio_features = track_manager.set_audio_features(track_list)
    assert len(tracks_with_audio_features) == len(track_list)
    for track in tracks_with_audio_features:
        assert track.features is not None


def test_dump(tmp_path, playlist_1_tracks):
    track_manager = TrackManager(None)
    track_manager.dump(playlist_1_tracks, filepath=tmp_path / "tracks.json")


def test_compute_tsne(audio_feature):
    track_manager = TrackManager(None)
    track = TrackData(
        name="test_track",
        id="id",
        uri="spotify:track:id",
        duration_ms=1000,
        popularity=50,
        features=TrackFeaturesData.parse_obj(audio_feature),
    )
    track_manager.compute_tsne([track, track])


def test_compute_tsne_without_features():
    track_manager = TrackManager(None)
    track = TrackData(
        name="test_track", id="id", uri="spotify:track:id", duration_ms=1000, popularity=50, features=None
    )
    with pytest.raises(ValueError):
        track_manager.compute_tsne([track, track])
