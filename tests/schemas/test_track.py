from datetime import date, datetime

import pytest

from chopin.schemas.track import TrackData


@pytest.mark.parametrize(
    "input_datetime, expected_date",
    [
        (datetime(2024, 12, 12, 12, 0, 0), date(2024, 12, 12)),
        (datetime(1970, 10, 10, 22, 56, 0), date(1970, 10, 10)),
        (None, None),
        (datetime(1900, 1, 5), date(1900, 1, 5)),
        (date(2022, 10, 8), date(2022, 10, 8)),
    ],
)
def test_trackdata_added_at_validator(spotify_track, input_datetime, expected_date):
    track = TrackData.model_validate(dict(added_at=input_datetime, **spotify_track))
    assert track.added_at == expected_date
