"""Date range utilitaries."""
from datetime import datetime
from typing import TypeAlias

ReleaseRange: TypeAlias = tuple[datetime, datetime]


def read_date(date: tuple[str | None, str | None] | None) -> ReleaseRange | None:
    """Read a date from  a string tuple.

    Args:
        date: The date to parse

    Returns:
        A parsed date (if it exists), e.g. a range of two datetime objects.

    Examples:
        >>> read_date('10/01/2023', '10/02/2023')
        (datetime.datetime(2023, 1, 10, 0, 0), datetime.datetime(2023, 2, 10, 0, 0))
        >>> read_date('10/01/2023', )
        (datetime.datetime(2023, 1, 10, 0, 0), datetime.datetime.now()
    """
    _format = "%d/%m/%Y"
    match date:
        case None:
            return date
        case (str(), str()):
            return datetime.strptime(date[0], _format), datetime.strptime(date[1], _format)
        case (str(), None):
            return datetime.strptime(date[0], _format), datetime.now()
        case (None, str()):
            return datetime.strptime("01/01/1900", _format), datetime.strptime(date[1], _format)


def parse_release_date(date: str) -> datetime:
    """Parse the release date depending on the level of detail available.

    Args:
        date: An input date, as a string

    Returns:
        A formatted date, with the datetime library.
    """
    if not date:
        return datetime(1970, 1, 1, 0, 0)
    match len(date):
        case 4:
            _format = "%Y"
        case 7:
            _format = "%Y-%m"
        case 10:
            _format = "%Y-%m-%d"
        case 19:
            _format = "%Y-%m-%dT%M:%S:%f"
        case _ :
            raise ValueError(f"Bad release date format: {date}")
    return datetime.strptime(date, _format)
