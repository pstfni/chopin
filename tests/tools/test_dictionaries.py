import pytest

from chopin.tools.dictionaries import flatten_dict


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
