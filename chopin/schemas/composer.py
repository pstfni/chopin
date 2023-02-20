import math
from typing import List, Literal, Optional

import numpy as np
from pydantic import BaseModel, ValidationError, confloat, conint, conlist, root_validator, validator

from chopin.utils import get_logger

logger = get_logger(__name__)


class ComposerConfigItem(BaseModel):
    """Base schema for input in the composer configuration.

    Attributes:
        name: Name of the item. It should respect the simplify_string nomenclature
        weight: Weight of the input in the final composition
    """

    name: str
    weight: confloat(ge=0) = 1
    nb_songs: Optional[int] = 0


class ComposerConfigRecommendation(ComposerConfigItem):
    """Base schema for recommendation inputs in the composer configuration.

    Attributes:
        name: Name of the feature to recommend.
        value: Target value to recommend
    """

    name: Literal[
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "loudness",
        "speechiness",
        "tempo",
        "popularity",
        "valence",
    ]
    value: float  # relaxed constraint. todo: see if we can have constraint based on feature type (or add validators)

    @validator("name")
    def update_name_with_spotify_feature_format(cls, v):
        return f"feature_{v}"


class ComposerConfigListeningHistory(BaseModel):
    """Base schema for the configuration section which will add the current user's best songs.

    Attributes:
        time_range: Time criteria for the best tracks. One of short_term (~ last 4 weeks), medium_term (~ last 6 months)
            or long_term (~ all time).
        weight: Weight of the input in the final composition
    """

    time_range: Literal["short_term", "medium_term", "long_term"] = "short_term"
    weight: confloat(ge=0) = 1
    nb_songs: Optional[int] = 0


class ComposerConfig(BaseModel):
    """Schema for a composer configuration.

    Attributes:
        name: Name of the playlist you wish to create
        description: Description for your playlist
        nb_songs: Target number of songs for the playlist.
        playlists: A list of playlist names and their weight
        artists: A list of artists from which to pick songs, and their weight in the final composition
        features: A list of features and their value, to add recommendations based on recent listening
        radios: A list of artists from which to pick related songs.
        uris: A list of spotify playlist URIs to pick from directly.
    """

    name: str = "🤖 Robot Mix"
    description: str = "Randomly generated mix"
    nb_songs: conint(gt=0)
    playlists: Optional[List[ComposerConfigItem]] = []
    artists: Optional[List[ComposerConfigItem]] = []
    features: Optional[conlist(ComposerConfigRecommendation, max_items=5)] = []
    history: Optional[conlist(ComposerConfigListeningHistory, max_items=3)] = []
    radios: Optional[List[ComposerConfigItem]] = []
    uris: Optional[List[ComposerConfigItem]] = []

    @validator("history")
    def history_field_ranges_must_be_unique(cls, v):
        ranges = [item.time_range for item in v]
        if len(set(ranges)) != len(ranges):
            raise ValidationError("time_range items for history must be unique")
        return v

    @root_validator
    def fill_nb_songs(cls, values):
        """From the nb_songs and item weights, compute the nb_songs of each item.

        Args:
            values: Attributes of the composer configuration model.
        """
        categories = {"playlists", "artists", "features", "history", "radios", "uris"}
        item_weights: List[float] = [item.weight for category in categories for item in values.get(category)]
        sum_of_weights: float = np.array(list(item_weights)).sum()
        total_nb_songs: int = 0
        for category in categories:
            for item in values.get(category):
                item.nb_songs = math.ceil((item.weight / sum_of_weights) * values["nb_songs"])
                total_nb_songs += item.nb_songs
        logger.info(f"With the composer configuration parsed, {total_nb_songs} songs will be added.")
        return values