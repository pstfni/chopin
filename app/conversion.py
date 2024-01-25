"""Logic to convert streamlit form data to chopin configuration objects."""
from typing import Literal

import pandas as pd

from chopin.schemas.composer import (
    ComposerConfig,
    ComposerConfigItem,
    ComposerConfigListeningHistory,
    ComposerConfigRecommendation,
)


def _convert_form_to_item(form: pd.DataFrame) -> list[ComposerConfigItem]:
    """Convert a dataframe gotten from the streamlit form into valid items for playlist composition.

    Args:
        form: The user input in the Streamlit app, exported as a dataframe.

    Returns:
        Items for the playlist composition.
    """
    return [ComposerConfigItem(**item) for item in form.to_dict(orient="records")]


def _convert_feature_to_item(feature_form: pd.DataFrame) -> list[ComposerConfigRecommendation]:
    return [ComposerConfigRecommendation(**item) for item in feature_form.to_dict(orient="records")]


def _convert_history_to_item(
    history_options: list[Literal["long_term", "medium_term", "short_term"]],
) -> list[ComposerConfigListeningHistory]:
    """Convert the list of history options selected by the user into proper items for the composer configuration.

    Args:
        history_options: User selected ranges for its listening history.

    Returns:
        A list of composer config items ready to be added to the main configuration.
    """
    return [ComposerConfigListeningHistory(time_range=option) for option in history_options]


def convert_form_configuration(
    composer_configuration: ComposerConfig,
    *,
    playlist_config: pd.DataFrame,
    artist_config: pd.DataFrame,
    radio_config: pd.DataFrame,
    uri_config: pd.DataFrame,
    genres_config: pd.DataFrame,
    features_config: pd.DataFrame,
    history_config: ComposerConfigListeningHistory,
) -> ComposerConfig:
    """Take a composer configuration and fill its source attributes with configurations for each items.

    Args:
        composer_configuration: A composer configuration.
        playlist_config: A form configuration for the playlist sources.
        artist_config: A form configuration for the artist sources.
        radio_config: A form configuration for the radio sources.
        uri_config: A form configuration for uri sources.
        genres_config: A form configuration for the genres sources.
        features_config: A form configuration for the features sources.
        history_config: A form configuration for the history sources.

    Returns:
        An updated composer configuration.

    Notes:
        Try it with Annotated[form, _convert...] ?
    """
    composer_config = composer_configuration.model_copy()
    composer_config.playlists = _convert_form_to_item(playlist_config)
    composer_config.artists = _convert_form_to_item(artist_config)
    composer_config.radios = _convert_form_to_item(radio_config)
    composer_config.uris = _convert_form_to_item(uri_config)
    composer_config.genres = _convert_form_to_item(genres_config)
    composer_config.features = _convert_feature_to_item(features_config)
    composer_config.history = _convert_history_to_item(history_config)
    return composer_config
