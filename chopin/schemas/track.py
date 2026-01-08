"""Pydantic schemas for tracks."""

from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel

from chopin.schemas.album import AlbumData
from chopin.schemas.artist import ArtistData
from chopin.tools.dictionaries import flatten_dict


def datetime_to_date(dt: datetime | date | None) -> date | None:
    """Truncate a datetime object into its date object."""
    if dt and isinstance(dt, datetime):
        return dt.date()
    return dt


FormattedDate = Annotated[datetime | date | None, AfterValidator(datetime_to_date)]


class TrackData(BaseModel):
    """Representation of a track.

    Attributes:
        name: Track name
        id: Track id
        uri: Spotify URI for the track
        duration_ms: Duration of the track, in milliseconds
        popularity: A [0, 100] measure for the track popularity. 100 is most popular
        added_at: A date, when available, for which the track was added in the playlist.
        album: The album data
        artists: The artists on the track
        features: Audio features of the track.

    !!! warning
        By default, tracks sent by the Spotify API do not contain audio feature information.
        A call to the dedicated endpoint is necessary to fill the attribute.
    """

    name: str
    id: str
    uri: str
    duration_ms: int
    popularity: int
    added_at: FormattedDate | None = None
    album: AlbumData | None = None
    artists: list[ArtistData] | None = None
    popularity: int | None = 0

    def to_flatten_dict(self, **kwargs):
        """Export the track data as a non-nested dictionary."""
        if isinstance(self.artists, list):
            self.artists = self.artists[0]
        return flatten_dict(self.model_dump(**kwargs))
