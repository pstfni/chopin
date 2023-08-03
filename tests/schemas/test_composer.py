import pytest
from pydantic import ValidationError

from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigRecommendation


def test_fill_nb_songs():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 200,
        "playlists": [{"name": "rock", "weight": 1}, {"name": "folk", "weight": 2}],
        "artists": [{"name": "Bruce Springsteen", "weight": 0.5}, {"name": "Soprano", "weight": 0}],
    }
    out = ComposerConfig.model_validate(composer_config)
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
    ComposerConfig.model_validate(composer_config)

    # problemo
    bad_composer_config = {
        "nb_songs": 100,
        "history": [{"time_range": "short_term"}, {"time_range": "short_term"}, {"time_range": "long_term"}],
    }
    with pytest.raises(ValidationError):
        ComposerConfig.model_validate(bad_composer_config)


def test_fill_nb_songs_with_history():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 100,
        "playlists": [{"name": "rock", "weight": 1}],
        "history": [{"time_range": "short_term", "weight": 1}],
    }
    out = ComposerConfig.model_validate(composer_config)
    assert out.playlists[0].nb_songs == 50
    assert out.history[0].nb_songs == 50
    assert out.artists == []


@pytest.mark.parametrize(
    "recommendation_item, expected_item",
    [
        # Make sure enumeration with value works
        (
            {
                "name": "acousticness",
                "value": 0.8,
                "weight": 0.1,
            },
            {
                "name": "acousticness",
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
    assert out.model_dump() == expected_item


@pytest.mark.parametrize(
    "uri_item, expected_item",
    [
        # Default case: uri
        ({"name": "37i9dQZF1DWWv8B5EWK7bn"}, {"name": "37i9dQZF1DWWv8B5EWK7bn", "weight": 1, "nb_songs": 0}),
        # Validated case: link becomes uri
        (
            {"name": "https://open.spotify.com/playlist/37i9dQZF1DWWv8B5EWK7bn?si=8d52c3fef8d74064"},
            {"name": "37i9dQZF1DWWv8B5EWK7bn", "weight": 1, "nb_songs": 0},
        ),
        # Bad input case: nothing happpens
        ({"name": "d$fd5f_not_an^$$$uri"}, {"name": "d$fd5f_not_an^$$$uri", "weight": 1, "nb_songs": 0}),
        # Empty input case
        ({"name": ""}, {"name": "", "weight": 1, "nb_songs": 0}),
    ],
)
def test_composer_config_uri_item(uri_item, expected_item):
    out = ComposerConfigItem(**uri_item)
    assert out.model_dump() == expected_item
