import pandas as pd

from chopin import VERSION
from chopin.schemas.playlist import PlaylistSummary


def test_playlist_summary(playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    assert len(playlist_summary.tracks) == playlist_summary._nb_tracks
    # All tracks have a 50 popularity and a 1000ms duration in the fixture
    assert playlist_summary._avg_popularity == 50
    assert playlist_summary._total_duration == 1000 * len(playlist_summary.tracks)
    assert playlist_summary._nb_artists == 50


def test_playlist_summary_serialization(playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    serialized = playlist_summary.model_dump()

    assert "version" in serialized
    assert serialized["version"] == VERSION
    assert PlaylistSummary.model_validate(serialized)


def test_playlist_to_dataframe(playlist_1, playlist_1_tracks):
    playlist_summary = PlaylistSummary(playlist=playlist_1, tracks=playlist_1_tracks)
    df = playlist_summary.to_dataframe()
    assert len(df) == 50
    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "artists"] == "test_artist_p_0"
