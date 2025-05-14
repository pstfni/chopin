import pytest
from pydantic import ValidationError

from chopin.managers.selection import SelectionMethod
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem


def test_fill_nb_songs():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 200,
        "playlists": [{"name": "rock", "weight": 1}, {"name": "folk", "weight": 2}],
    }
    out = ComposerConfig.model_validate(composer_config)
    assert out.playlists[0].nb_songs == 67
    assert out.playlists[1].nb_songs == 134
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
    assert out.uris == []


@pytest.mark.parametrize(
    "uri_item, expected_item",
    [
        # Default case: uri
        (
            {"name": "37i9dQZF1DWWv8B5EWK7bn"},
            {"name": "37i9dQZF1DWWv8B5EWK7bn", "weight": 1, "nb_songs": 0},
        ),
        # Validated case: link becomes uri
        (
            {"name": "https://open.spotify.com/playlist/37i9dQZF1DWWv8B5EWK7bn?si=8d52c3fef8d74064"},
            {"name": "37i9dQZF1DWWv8B5EWK7bn", "weight": 1, "nb_songs": 0},
        ),
        # Bad input case: nothing happpens
        (
            {"name": "d$fd5f_not_an^$$$uri"},
            {"name": "d$fd5f_not_an^$$$uri", "weight": 1, "nb_songs": 0},
        ),
        # Empty input case
        ({"name": ""}, {"name": "", "weight": 1, "nb_songs": 0}),
    ],
)
def test_composer_config_uri_item(uri_item, expected_item):
    out = ComposerConfigItem(**uri_item)
    assert out.model_dump(exclude={"selection_method"}) == expected_item


@pytest.mark.parametrize(
    "selection_input, expected_output",
    [
        ("original", SelectionMethod.ORIGINAL),
        ("popularity", SelectionMethod.POPULARITY),
        ("PoPULARIty", SelectionMethod.POPULARITY),
        ("Random", SelectionMethod.RANDOM),
        ("Latest", SelectionMethod.LATEST),
        ("latest", SelectionMethod.LATEST),
    ],
)
def test_composer_config_item_selection_method(selection_input, expected_output):
    item = ComposerConfigItem(
        name="playlist",
        weight=2,
        selection_method=selection_input,
    )
    assert item.selection_method == expected_output


def test_composer_config_item_default_selection_method():
    item = ComposerConfigItem(
        name="name",
        weight=1,
    )
    assert item.selection_method == SelectionMethod.RANDOM
