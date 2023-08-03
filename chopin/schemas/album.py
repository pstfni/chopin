"""Pydantic schemas for albums."""
from datetime import datetime

from pydantic import BaseModel, field_validator


class AlbumData(BaseModel):
    """Album data representation.

    Attributes:
        name: Album name
        id: Album id
        uri: Spotify URI for the album
        release_date: The year the album was released.
    """

    name: str
    id: str
    uri: str
    release_date: str | int

    @field_validator("release_date", mode="before")
    def parse_release_date(cls, v):
        """Format the release date based on the level of detail available."""
        if isinstance(v, str):
            if len(v) == 10:
                format = "%Y-%m-%d"
            elif len(v) == 7:
                format = "%Y-%m"
            else:
                format = "%Y"
            return datetime.strptime(v, format).year
        return v.year
