"""Pydantic schemas for artists."""
from pydantic import BaseModel


class ArtistData(BaseModel):
    """Artist data representation.

    Attributes:
    ----------
        name: Name of the artist
        id: Id of the artist
        uri: Spotify URI for the artist
        genres: A list of strings describing the artist genres

    !!! warning
        The 'genres' information is not always available. And it can be quite flaky
    """

    name: str
    id: str
    uri: str
    genres: list[str] | None

    class Config:
        extra = "ignore"
