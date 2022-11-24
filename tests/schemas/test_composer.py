from schemas.composer import ComposerConfig


# todo: fixture, parametrize and more test cases
def test_fill_nb_songs():
    composer_config = {
        "name": "test_playlist",
        "nb_songs": 200,
        "playlists": [{"name": "rock", "weight": 1}, {"name": "folk", "weight": 2}],
        "artists": [{"name": "Bruce Springsteen", "weight": 0.5}, {"name": "Soprano", "weight": 0}],
    }
    out = ComposerConfig.parse_obj(composer_config)
    assert out.playlists[0].nb_songs == 57
    assert out.playlists[1].nb_songs == 114
    assert out.artists[0].nb_songs == 28
    assert out.artists[1].nb_songs == 0
    assert out.features == []
    assert out.description == "Randomly generated mix"
