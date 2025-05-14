"""Schemas for playlist composition."""

import math
from typing import Annotated, Literal

import numpy as np
from pydantic import AfterValidator, BaseModel, Field, computed_field, field_validator, model_validator

from chopin.managers.selection import SelectionMethod
from chopin.tools.dates import read_date
from chopin.tools.logger import get_logger
from chopin.tools.strings import extract_uri_from_playlist_link

logger = get_logger(__name__)
SOURCES = [
    "playlists",
    "history",
    "uris",
]


class ComposerConfigItem(BaseModel):
    """Base schema for input in the composer configuration.

    Attributes:
        name: Name of the item. It should respect the simplify_string nomenclature
        weight: Weight of the input in the final composition
    """

    name: Annotated[str, extract_uri_from_playlist_link]
    weight: Annotated[float, Field(ge=0)] = 1.0
    nb_songs: int | None = 0
    selection_method: SelectionMethod | None = SelectionMethod.RANDOM

    @field_validator("name", mode="before")
    def extract_uri_from_link(cls, v: str):
        """If the value is an https link to spotify, extract the URI data.

        This allow users to share full links to their playlists.
        """
        if v.startswith("https://open.spotify.com"):
            return extract_uri_from_playlist_link(v)
        return v

    @field_validator("selection_method", mode="before")
    def lower_case_selection_method(cls, selection_method: str) -> SelectionMethod:
        """Force the selection method to be lower case."""  # TODO address this with proper enum handling
        if selection_method:
            return selection_method.lower()
        return


class ComposerConfigListeningHistory(BaseModel):
    """Base schema for the configuration section which will add the current user's best songs.

    Attributes:
        time_range: Time criteria for the best tracks. One of short_term (~ last 4 weeks), medium_term (~ last 6 months)
            or long_term (~ all time).
        weight: Weight of the input in the final composition
    """

    time_range: Literal["short_term", "medium_term", "long_term"] = "short_term"
    weight: Annotated[float, Field(ge=0)] = 1
    nb_songs: int | None = 0


class ComposerConfig(BaseModel):
    """Schema for a composer configuration.

    Attributes:
        name: Name of the playlist you wish to create
        description: Description for your playlist
        nb_songs: Target number of songs for the playlist.
        playlists: A list of playlist names and their weight.
        uris: A list of spotify playlist URIs to pick from directly.
        history: Include past listening habits and most listened songs.
    """

    name: str = "🤖 Robot Mix"
    description: str = "Randomly generated mix"
    nb_songs: Annotated[int, Field(gt=0)]
    release_range: Annotated[tuple[str | None, str | None] | None, AfterValidator(read_date)] | None = None
    playlists: list[ComposerConfigItem] | None = []
    history: Annotated[list[ComposerConfigListeningHistory], Field(max_length=3)] | None = []
    uris: list[ComposerConfigItem] | None = []

    @field_validator("history")
    def history_field_ranges_must_be_unique(cls, v):
        """Check the history items are distinct."""
        ranges = [item.time_range for item in v]
        if len(set(ranges)) != len(ranges):
            raise ValueError("time_range items for history must be unique")
        return v

    @model_validator(mode="after")
    def fill_nb_songs(cls, values: "ComposerConfig") -> "ComposerConfig":
        """From the nb_songs and item weights, compute the nb_songs of each item.

        Args:
            values: Attributes of the composer configuration model.
        """
        item_weights: list[float] = [item.weight for category in SOURCES for item in getattr(values, category)]
        sum_of_weights: float = np.array(list(item_weights)).sum()
        total_nb_songs: int = 0
        for category in SOURCES:
            for item in getattr(values, category):
                item.nb_songs = math.ceil((item.weight / sum_of_weights) * values.nb_songs)
                total_nb_songs += item.nb_songs
        logger.info(f"With the composer configuration parsed, {total_nb_songs} songs will be added.")
        return values

    @computed_field
    def items(self) -> list[list[ComposerConfigItem]]:  # noqa: D102
        return {source: getattr(self, source) for source in SOURCES}.items()
