"""Pydantc schemas for users."""
from pydantic import BaseModel


class UserData(BaseModel):
    """User representation.

    Attributes:
    ----------
        name: Name of the user
        id: The user id
        uri: Spotify URI for the user
    """

    name: str
    id: str
    uri: str
