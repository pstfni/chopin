import pytest

from spotify_builder.utils import flatten_dict, flatten_list, match_strings, simplify_string


@pytest.mark.parametrize(
    "in_dictionary, expected_dictionary",
    [
        # Simple dict
        ({"key": "value", "version": 0}, {"key": "value", "version": 0}),
        # Dict with nested object
        (
            {"key": "value", "object": {"key": "value", "version": 0}},
            {"key": "value", "object.key": "value", "object.version": 0},
        ),
        # Dict with nested objects, and it goes deep. For now we don't support it
        ({"a": 1, "object": {"b": 2, "sub_object": {"c": 3}}}, {"a": 1, "object.b": 2, "object.sub_object": {"c": 3}}),
    ],
)
def test_flatten_dict(in_dictionary, expected_dictionary):
    out_dictionary = flatten_dict(in_dictionary)
    assert out_dictionary == expected_dictionary


@pytest.mark.parametrize(
    "in_list, expected_list",
    [
        ([], []),
        ([[0, 1, 2]], [0, 1, 2]),
        ([[0], [1, 2]], [0, 1, 2]),
        ([[0], [1], [2]], [0, 1, 2]),
    ],
)
def test_flatten_list(in_list, expected_list):
    out_list = flatten_list(in_list)
    assert out_list == expected_list


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
