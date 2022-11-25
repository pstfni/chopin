import math
from typing import List, Literal, Optional

import numpy as np
from pydantic import BaseModel, confloat, conint, conlist, root_validator, validator

from utils import get_logger

logger = get_logger(__name__)


class ComposerConfigItem(BaseModel):
    """Base schema for input in the composer configuration.

    Attributes:
        name: Name of the item. It should respect the simplify_string nomenclature
        weight: Weight of the input in the final composition
    """

    name: str
    weight: confloat(ge=0)
    nb_songs: Optional[int] = 0


class ComposerConfigRecommendation(ComposerConfigItem):
    """Base schema for recommendation inputs in the composer configuration.

    Attributes:
        name: Name of the feature to recommend.
        value: Target value to recommend
    """

    name: Literal[
        "acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "valence"
    ]
    value: confloat(ge=0, lt=1)

    @validator("name")
    def update_name_with_spotify_feature_format(cls, v):
        return f"feature_{v}"


class ComposerConfig(BaseModel):
    """Schema for a composer configuration.

    Attributes:
        name: Name of the playlist you wish to create
        description: Description for your playlist
        nb_songs: Target number of songs for the playlist.
        playlists: A list of playlist names and their weight
        artists: A list of artists from which to pick songs, and their weight in the final composition
        features: A list of features and their value, to add recommendations based on recent listening
    """

    name: str = "🤖 Robot Mix"
    description: str = "Randomly generated mix"
    nb_songs: conint(gt=0)
    playlists: Optional[List[ComposerConfigItem]] = []
    artists: Optional[List[ComposerConfigItem]] = []
    features: Optional[conlist(ComposerConfigRecommendation, max_items=5)] = []

    @root_validator
    def fill_nb_songs(cls, values):
        """From the nb_songs and item weights, compute the nb_songs of each item.

        Args:
            values: Attributes of the composer configuration model.
        """
        item_weights: List[float] = [
            item.weight for category in ["playlists", "artists", "features"] for item in values.get(category)
        ]
        sum_of_weights: float = np.array(list(item_weights)).sum()
        total_nb_songs: int = 0
        for category in {"playlists", "artists", "features"}:
            for item in values.get(category):
                item.nb_songs = math.ceil((item.weight / sum_of_weights) * values["nb_songs"])
                total_nb_songs += item.nb_songs
        logger.info(f"With the composer configuration parsed, {total_nb_songs} will be added.")
        return values
