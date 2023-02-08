from unittest.mock import MagicMock

import pytest

from spotify_builder.managers.recommendation import RecommendationManager, _generate_target_features
from spotify_builder.schemas.base import TrackData, TrackFeaturesData
from tests.conftest import artist_data, track_data


def side_effect_recommendations(seed_tracks, seed_artists, seed_genres, limit, **kwargs):
    tracks = [track_data(str(i)) for i in range(limit)]
    return tracks


@pytest.mark.parametrize("max_recommendations", [0, 50])
@pytest.mark.parametrize(
    "seed_artists, seed_tracks, seed_genres",
    [
        # One of each, everything is OK
        (["id:0"], ["id:1"], ["id:2"]),
        # Only artists, everything is OK
        (["id:0", "id:1", "id:2"], None, None),
        # Three artists, two tracks and a genre: more than 5 seeds -> we return a value error.
        pytest.param(["id:0", "id:1", "id:2"], ["id:0", "id:1"], ["id:1"], marks=pytest.mark.xfail(raises=ValueError)),
    ],
)
def test_get_recommendations(max_recommendations, seed_artists, seed_tracks, seed_genres, mock_client_manager):
    recommendation_manager = RecommendationManager(mock_client_manager)
    mock_client_manager.get_recommendations = MagicMock(side_effect=side_effect_recommendations)

    recs = recommendation_manager.get_recommendations(max_recommendations)
    # Can't get more than 100 recommendations
    assert len(recs) == max_recommendations
    if recs:
        assert isinstance(recs[0], TrackData)


@pytest.mark.parametrize("nb_artists", [2, 10, 20])
@pytest.mark.parametrize("max_recommendations", [0, 20])
@pytest.mark.parametrize("target_features", [None, TrackFeaturesData(acousticness=0.2)])
def test_get_recommendations_from_artists(nb_artists, max_recommendations, target_features, mock_client_manager):
    recommendation_manager = RecommendationManager(mock_client_manager)
    mock_client_manager.get_recommendations = MagicMock(side_effect=side_effect_recommendations)
    artists = [artist_data(str(i)) for i in range(nb_artists)]
    recs = recommendation_manager.get_recommendations_from_artists(
        max_recommendations=max_recommendations, target_features=target_features, artists=artists
    )
    # Can't get more than 100 recommendations
    assert len(recs) == max_recommendations
    if recs:
        assert isinstance(recs[0], TrackData)


@pytest.mark.parametrize("nb_tracks", [2, 10, 20])
@pytest.mark.parametrize("max_recommendations", [0, 20])
@pytest.mark.parametrize("target_features", [None, TrackFeaturesData(valence=0.2)])
def test_get_recommendations_from_tracks(nb_tracks, max_recommendations, target_features, mock_client_manager):
    recommendation_manager = RecommendationManager(mock_client_manager)
    mock_client_manager.get_recommendations = MagicMock(side_effect=side_effect_recommendations)
    tracks = [track_data(str(i)) for i in range(nb_tracks)]
    recs = recommendation_manager.get_recommendations_from_tracks(
        max_recommendations=max_recommendations, tracks=tracks, target_features=target_features
    )
    # Can't get more than 100 recommendations
    assert len(recs) == max_recommendations
    if recs:
        assert isinstance(recs[0], TrackData)


def test__generate_target_features(track_features_data):
    out = _generate_target_features(target_features=track_features_data)
    expected = {f"target_{name}": value for name, value in track_features_data.dict().items()}
    assert out == expected


def test__generate_target_features_with_few_features():
    track_features = TrackFeaturesData(acousticness=0.6, loudness=-0.4)
    out = _generate_target_features(track_features)
    expected = {
        "target_acousticness": 0.6,
        "target_loudness": -0.4,
    }
    assert out == expected
