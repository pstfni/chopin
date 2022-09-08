from unittest.mock import MagicMock

import pytest
from spotipy.client import Spotify

from managers.recommendation import RecommendationManager
from schemas import TrackData
from tests.conftest import spotify_track


def side_effect_recommendations(seed_tracks, seed_artists, seed_genres, limit):
    tracks = [spotify_track() for _ in range(limit)]
    return {"tracks": tracks}


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
def test_get_recommendations(max_recommendations, seed_artists, seed_tracks, seed_genres):
    mock_client = Spotify()
    mock_client.recommendations = MagicMock(side_effect=side_effect_recommendations)
    recommendation_manager = RecommendationManager(mock_client)

    recs = recommendation_manager.get_recommendations(max_recommendations)
    # Can't get more than 100 recommendations
    assert len(recs) == max_recommendations
    if recs:
        assert isinstance(recs[0], TrackData)
