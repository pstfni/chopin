import pytest

from chopin import VERSION
from chopin.schemas.playlist import PlaylistSummary
from chopin.schemas.track import TrackFeaturesData


def test_playlist_summary(playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    assert len(playlist_summary.tracks) == playlist_summary._nb_tracks
    # All tracks have a 50 popularity and a 1000ms duration in the fixture
    assert playlist_summary._avg_popularity == 50
    assert playlist_summary._total_duration == 1000 * len(playlist_summary.tracks)
    assert playlist_summary._nb_artists == 50
    # Check some features
    assert isinstance(playlist_summary._avg_features, TrackFeaturesData)
    pytest.approx(playlist_summary._avg_features.acousticness, 0.1, 1e-6)
    pytest.approx(playlist_summary._avg_features.liveness, 0.5, 1e-6)


def test_playlist_summary_serialization(playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    serialized = playlist_summary.model_dump()

    assert "version" in serialized
    assert serialized["version"] == VERSION
    assert PlaylistSummary.model_validate(serialized)
