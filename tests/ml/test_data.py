import datetime
import json
import random

import numpy as np
import pandas as pd
import pytest

from ml.data import format_records, format_track, normalize_features, read_playlist
from schemas import AlbumData, TrackData, TrackFeaturesData


@pytest.fixture
def track():
    return TrackData(
        name="test",
        id="1000",
        uri="test:1000",
        duration_ms="500",
        popularity="50",
        album=AlbumData(
            name="album_test", id="2000", uri="album_test:2000", release_date=datetime.datetime(1992, 12, 25)
        ),
        features=TrackFeaturesData(
            acousticness=-1,
            danceability=-0.8,
            energy=-0.6,
            instrumentalness=-0.4,
            liveness=-0.2,
            loudness=0.0,
            speechiness=0.2,
            valence=0.4,
            tempo=0.6,
            mode=1,
            key=1,
            analysis_url="url",
        ),
    )


@pytest.fixture
def track_2():
    return TrackData(
        name="another_test",
        id="2000",
        uri="test:2000",
        duration_ms="400",
        popularity="10",
        album=AlbumData(
            name="album_test", id="2000", uri="album_test:2000", release_date=datetime.datetime(1992, 12, 25)
        ),
        features=TrackFeaturesData(
            acousticness=-4,
            danceability=-3,
            energy=-2,
            instrumentalness=-1,
            liveness=-1,
            loudness=0.0,
            speechiness=1,
            valence=2,
            tempo=4,
            mode=1,
            key=1,
            analysis_url="url",
        ),
    )


def test_read_playlist(tmp_path, playlist_1_tracks):
    with open(tmp_path / "test.json", "w") as outfile:
        json.dump([track.to_flatten_dict() for track in playlist_1_tracks], outfile)
    name, tracks = read_playlist(tmp_path / "test.json")
    assert name == "test"
    assert tracks == playlist_1_tracks


def test_format_track(track):
    out = format_track(track)
    assert out == {
        "name": "test",
        "album.release_date": 1992,
        "features.acousticness": -1,
        "features.danceability": -0.8,
        "features.energy": -0.6,
        "features.instrumentalness": -0.4,
        "features.liveness": -0.2,
        "features.loudness": 0,
        "features.speechiness": 0.2,
        "features.valence": 0.4,
        "features.tempo": 0.6,
    }


@pytest.mark.parametrize(
    "split, expected_split",
    [
        (0.8, "train"),
        (1.0, "train"),
        (0.1, "validation"),
        pytest.param(0, None, marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(1.3, None, marks=pytest.mark.xfail(raises=ValueError)),
    ],
)
def test_format_records(track, split, expected_split):
    random.seed(1000)
    record = format_records(track, "test", split)
    assert record == {
        "name": "test",
        "album.release_date": 1992,
        "features.acousticness": -1,
        "features.danceability": -0.8,
        "features.energy": -0.6,
        "features.instrumentalness": -0.4,
        "features.liveness": -0.2,
        "features.loudness": 0,
        "features.speechiness": 0.2,
        "features.valence": 0.4,
        "features.tempo": 0.6,
        "playlist.name": "test",
        "split": expected_split,
    }


def test_normalize_features(track, track_2):
    track_df = pd.DataFrame.from_records([format_track(track), format_track(track_2)])
    out = normalize_features(track_df)
    for column_name in [
        "features.acousticness",
        "features.danceability",
        "features.energy",
        "features.instrumentalness",
        "features.liveness",
        "features.loudness",
        "features.speechiness",
        "features.valence",
        "features.tempo",
    ]:
        assert column_name in out.columns
    np.testing.assert_array_equal(out["features.acousticness"].values, [1.0, 0.0])
    np.testing.assert_array_equal(out["features.danceability"].values, [1.0, 0.0])
    np.testing.assert_array_equal(out["features.energy"].values, [1.0, 0.0])
    np.testing.assert_array_equal(out["features.instrumentalness"].values, [1.0, 0.0])
    np.testing.assert_array_equal(out["features.liveness"].values, [1.0, 0.0])
    np.testing.assert_array_equal(out["features.loudness"].values, [0.0, 0.0])
    np.testing.assert_array_equal(out["features.speechiness"].values, [0.0, 1.0])
    np.testing.assert_array_equal(out["features.valence"].values, [0.0, 1.0])
    np.testing.assert_array_equal(out["features.tempo"].values, [0.0, 1.0])
