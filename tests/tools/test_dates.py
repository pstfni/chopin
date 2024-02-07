from datetime import datetime, timedelta

from chopin.tools.dates import read_date, parse_release_date
import pytest


def test_read_date_with_valid_dates():
    date = ("10/01/2023", "10/02/2023")
    result = read_date(date)
    assert result == (datetime(2023, 1, 10, 0, 0), datetime(2023, 2, 10, 0, 0))


def test_read_date_right_open():
    date = ("10/01/2023", None)
    result = read_date(date)
    assert result[0] == datetime(2023, 1, 10, 0, 0)
    # mocking datetime.now is a nightmare apparently ....
    assert datetime.now() - result[1] < timedelta(seconds=1)


def test_read_date_left_open():
    date = (None, "10/02/2023")
    result = read_date(date)
    assert result == (datetime(1900, 1, 1, 0, 0), datetime(2023, 2, 10, 0, 0))


def test_read_date_none():
    result = read_date(None)
    assert not result


@pytest.mark.parametrize(
    "input, expected",
    [
        ("1999-02", datetime(1999, 2, 1, 0, 0)),
        ("1999-10-01", datetime(1999, 10, 1, 0, 0)),
        ("1999", datetime(1999, 1, 1, 0, 0)),
        ("1986-02-03T10:00:00", datetime(1986, 2, 3, 0, 10)),
        (None, datetime(1970, 1, 1, 0, 0)),
        ("", datetime(1970, 1, 1, 0, 0))
    ],
)
def test_parse_release_date(input, expected):
    assert expected == parse_release_date(input)


@pytest.mark.parametrize(
    "input",
    [
        "1999/01/01",
        "23",
        "1999-01/02",
        "1999-01-02T00",
    ],
)
def test_parse_release_date_invalid_date(input):
    with pytest.raises(ValueError):
        parse_release_date(input)
