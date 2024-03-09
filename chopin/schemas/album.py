"""Pydantic schemas for albums."""
from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from chopin.tools.dates import parse_release_date


class AlbumData(BaseModel):
    """Album data representation.

    Attributes:
        name: Album name
        id: Album id
        uri: Spotify URI for the album
        release_date: The year the album was released.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    id: str
    uri: str
    release_date: date | str

    @field_validator("release_date", mode="before")
    def release_date_validate(cls, v):
        """Format the release date based on the level of detail available."""
        if isinstance(v, str):
            return parse_release_date(v)
