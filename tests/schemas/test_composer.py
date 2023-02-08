import pytest
from pydantic import ValidationError

from icai.schemas.composer import ComposerConfig, ComposerConfigRecommendation


def test_fill_nb_songs():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 200,
        "playlists": [{"name": "rock", "weight": 1}, {"name": "folk", "weight": 2}],
        "artists": [{"name": "Bruce Springsteen", "weight": 0.5}, {"name": "Soprano", "weight": 0}],
    }
    out = ComposerConfig.parse_obj(composer_config)
    assert out.playlists[0].nb_songs == 58
    assert out.playlists[1].nb_songs == 115
    assert out.artists[0].nb_songs == 29
    assert out.artists[1].nb_songs == 0
    assert out.features == []
    assert out.description == "Randomly generated mix"


def test_history_field_ranges_must_be_unique():
    # no problemo
    composer_config = {
        "nb_songs": 100,
        "history": [{"time_range": "short_term"}, {"time_range": "medium_term"}, {"time_range": "long_term"}],
    }
    ComposerConfig.parse_obj(composer_config)

    # problemo
    bad_composer_config = {
        "nb_songs": 100,
        "history": [{"time_range": "short_term"}, {"time_range": "short_term"}, {"time_range": "long_term"}],
    }
    with pytest.raises(ValidationError):
        ComposerConfig.parse_obj(bad_composer_config)


def test_fill_nb_songs_with_history():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 100,
        "playlists": [{"name": "rock", "weight": 1}],
        "history": [{"time_range": "short_term", "weight": 1}],
    }
    out = ComposerConfig.parse_obj(composer_config)
    assert out.playlists[0].nb_songs == 50
    assert out.history[0].nb_songs == 50
    assert out.artists == []


@pytest.mark.parametrize(
    "recommendation_item, expected_item",
    [
        # Make sure renaming works
        (
            {
                "name": "acousticness",
                "value": 0.8,
                "weight": 0.1,
            },
            {
                "name": "feature_acousticness",
                "value": 0.8,
                "weight": 0.1,
                "nb_songs": 0,
            },
        ),
        # We dont accept weird stuff
        (
            pytest.param(
                {"name": "blah", "value": 0.8, "weight": 0.1}, None, marks=pytest.mark.xfail(raises=ValidationError)
            )
        ),
    ],
)
def test_composer_config_recommendation_item(recommendation_item, expected_item):
    out = ComposerConfigRecommendation(**recommendation_item)
    assert out.dict() == expected_item
