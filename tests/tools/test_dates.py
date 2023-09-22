from datetime import datetime, timedelta

from chopin.tools.dates import read_date


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
