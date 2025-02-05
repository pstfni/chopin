"""Logic to convert streamlit form data to chopin configuration objects."""

from typing import Literal

import pandas as pd

from chopin.schemas.composer import (
    ComposerConfig,
    ComposerConfigItem,
    ComposerConfigListeningHistory,
)


def _convert_form_to_item(form: pd.DataFrame) -> list[ComposerConfigItem]:
    """Convert a dataframe gotten from the streamlit form into valid items for playlist composition.

    Args:
        form: The user input in the Streamlit app, exported as a dataframe.

    Returns:
        Items for the playlist composition.
    """
    return [ComposerConfigItem(**item) for item in form.to_dict(orient="records")]


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
    radios_config: pd.DataFrame,
    uri_config: pd.DataFrame,
    mix_config: pd.DataFrame,
    history_config: ComposerConfigListeningHistory,
) -> ComposerConfig:
    """Take a composer configuration and fill its source attributes with configurations for each items.

    Args:
        composer_configuration: A composer configuration.
        playlist_config: A form configuration for the playlist sources.
        artist_config: A form configuration for the artist sources.
        radios_config: A form configuration for the radios sources.
        uri_config: A form configuration for uri sources.
        mix_config: A form configuration for genre sources.
        history_config: A form configuration for the history sources.

    Returns:
        An updated composer configuration.

    Notes:
        Try it with Annotated[form, _convert...] ?
    """
    composer_config = composer_configuration.model_copy()
    composer_config.playlists = _convert_form_to_item(playlist_config)
    composer_config.artists = _convert_form_to_item(artist_config)
    composer_config.radios = _convert_form_to_item(radios_config)
    composer_config.uris = _convert_form_to_item(uri_config)
    composer_config.mixes = _convert_form_to_item(mix_config)
    composer_config.history = _convert_history_to_item(history_config)
    return composer_config
