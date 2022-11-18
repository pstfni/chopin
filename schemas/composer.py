from pydantic import BaseModel, confloat, conint, conlist, root_validator
from typing import List, Literal, Optional


class _ComposerConfigItem(BaseModel):
    """
    Base schema for input in the composer configuration.

    Attributes:
        name: Name of the item. It should respect the simplify_string nomenclature
        weight: Weight of the input in the final composition
    """
    name: str
    weight: confloat(ge=0)
    nb_songs: Optional[int] = 0


class _ComposerConfigRecommendation(_ComposerConfigItem):
    """
    Base schema for recommendation inputs in the composer configuration.

    Attributes:
        name: Name of the feature to recommend.
        value: Target value to recommend
    """
    name: Literal["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "valence"]
    value: confloat(ge=0, lt=1)


class ComposerConfig(BaseModel):
    """
    Schema for a composer configuration.

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
    playlists: Optional[List[_ComposerConfigItem]] = []
    artists: Optional[List[_ComposerConfigItem]] = []
    features: Optional[conlist(_ComposerConfigRecommendation, max_items=5)] = []

    @root_validator
    def fill_nb_songs(cls, values):
        """
        From the nb_songs and item weights, compute the nb_songs of each item.
        """

