import pytest

from chopin.tools.strings import extract_uri_from_playlist_link, match_strings, owner_is_spotify, simplify_string


@pytest.mark.parametrize(
    "input_string, expected_string",
    [
        # empty string
        ("", ""),
        # simple string
        ("simple string", "simplestring"),
        # String with emojis
        ("string with 🐒", "stringwith"),
        # Uppercase
        ("String", "string"),
        # Trailing characters
        ("     string    ", "string"),
        # & characters are replaced by _. ' characters are ignored.
        ("string & ol'string", "string_olstring"),
        # Real Life scenario
        ("🎤Rock 60's", "rock60s"),
        # Real Life scenario #2
        ("🧢Hip-Hop & Rap", "hip-hop_rap"),
    ],
)
def test_simplify_string(input_string, expected_string):
    output_string = simplify_string(input_string)
    assert output_string == expected_string


@pytest.mark.parametrize(
    "input_strings, expected_result",
    [
        ([], True),
        (["etienne"], True),
        (["etienne", "EtiennE"], True),
        (["etienne", "étienne", "Etienne"], True),
        (["étienne", "etienne"], True),
        (["etienne", "Daho"], False),
        (["etienne😀", "etienne"], False),
    ],
)
def test_match_strings(input_strings, expected_result):
    assert match_strings(input_strings) == expected_result


@pytest.mark.parametrize(
    "input_link, expected_uri",
    [
        ("", ""),
        ("https://open.spotify.com/playlist/37i9dQZF1DWWv8B5EWK7bn?si=8d52c3fef8d74064", "37i9dQZF1DWWv8B5EWK7bn"),
        ("https://open.spotify.com/playlist/2ZdqnoI2DcFMqTfIaLnbss?si=c4c4244a4488423b", "2ZdqnoI2DcFMqTfIaLnbss"),
        ("https://open.spotify.com/playlist/aplaylistthatdonotfollowtheuriformat", ""),
    ],
)
def test_extract_uri_from_playlist_link(input_link: str, expected_uri: str):
    assert extract_uri_from_playlist_link(input_link) == expected_uri


@pytest.mark.parametrize(
    "uri, expected_result",
    [
        ("5oXFlMFTmq3LvXXQCrpMB6", False),
        ("3x0CugroW1F8VavVeBMFlZ", False),
        ("37i9dQZF1DZ06evO1S7maQ", True),
    ],
)
def test_owner_is_spotify(uri, expected_result):
    assert owner_is_spotify(uri) == expected_result
