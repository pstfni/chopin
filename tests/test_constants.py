import pytest

from chopin.constants import constants


def test_immutable_constants():
    with pytest.raises(AttributeError):
        constants.MAX_SEEDS = 10
