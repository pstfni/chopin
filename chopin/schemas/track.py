"""Pydantic schemas for tracks."""

from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict

from chopin.schemas.album import AlbumData
from chopin.schemas.artist import ArtistData
from chopin.tools.dictionaries import flatten_dict


def datetime_to_date(dt: datetime | date | None) -> date | None:
    """Truncate a datetime object into its date object."""
    if dt and isinstance(dt, datetime):
        return dt.date()
    return dt


FormattedDate = Annotated[datetime | date | None, AfterValidator(datetime_to_date)]


class TrackFeaturesData(BaseModel):
    """Track audio features representation.

    Attributes:
        acousticness: A [0., 1.] value indicating how acoustic the track is. 1 is most acoustic
        danceability: A [0., 1.] value for how suitable the track is for dancing. 1 is most danceable
        energy: A [0., 1.] measure of intensity and activity. 1 feel fast, loud and noisy
        instrumentalness: A [0., 1.] value indicating if the track contains vocals. 1 means no vocal content
        liveness: A [0., 1.] confidence score for whether the track was captured in a live setting. 1 is performed live.
        loudness: A decibel value for how loud the track is. Typically range between -60 and 0db for the loudest tracks.
        speechiness: A [0., 1.] measure for spoken words presence in a track. 1 is a talk show
        valence: A [0., 1.] score for the "positiveness" conveyed by the track. 1 are joyful songs.
        tempo: Beats per minute of a track.
        mode: Track modality. 0 is minor, 1 is major.
        key: Pitch Class Notation for the track key. -1 indicates that no key was detected.
        analysis_url: URL for the spotify page of the audio feature analysis.
    """

    acousticness: float | None = None
    danceability: float | None = None
    energy: float | None = None
    instrumentalness: float | None = None
    liveness: float | None = None
    loudness: float | None = None
    speechiness: float | None = None
    valence: float | None = None
    tempo: float | None = None
    mode: float | None = None
    key: float | None = None
    analysis_url: str | None = None

    model_config = ConfigDict(extra="ignore")


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
    features: TrackFeaturesData | None = None

    def to_flatten_dict(self, **kwargs):
        """Export the track data as a non-nested dictionary."""
        if isinstance(self.artists, list):
            self.artists = self.artists[0]
        return flatten_dict(self.model_dump(**kwargs))
