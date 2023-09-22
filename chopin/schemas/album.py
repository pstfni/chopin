"""Pydantic schemas for albums."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


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
    release_date: datetime

    @field_validator("release_date", mode="before")
    def parse_release_date(cls, v):
        """Format the release date based on the level of detail available."""
        _format = "%Y"
        if isinstance(v, str):
            if len(v) >= 7:
                _format = "%Y-%m"
            if len(v) >= 10:
                _format = "%Y-%m-%d"

        return datetime.strptime(v, _format)
