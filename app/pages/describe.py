"""Streamlit page for the describe endpoint and displaying its results."""

import json
from functools import lru_cache
from pathlib import Path

import streamlit as st
from requests import ConnectionError, HTTPError

from app.widgets import (
    _download_playlist_widget,
    _get_average_feature_widget,
    _get_dataframe_widget,
    _get_distribution_feature_widget,
    _get_nb_artists_widget,
    _get_nb_tracks_widget,
    _get_top_artist_widget,
)
from chopin.client.playlists import get_named_playlist, get_user_playlists
from chopin.constants import constants
from chopin.managers.playlist import summarize_playlist
from chopin.schemas.composer import TrackFeature
from chopin.schemas.playlist import PlaylistSummary


def get_feature(playlist: PlaylistSummary, feature_name: str) -> list[float]:
    """Parse the playlist tracks and return the values of the given feature.

    Args:
        playlist: The playlist to parse
        feature_name: The feature of interest

    Returns:
        An array of floats representing each track's feature.
    """
    return [getattr(track.features, feature_name) for track in playlist.tracks]


@lru_cache(maxsize=4)
def get_playlist(playlist_name: str, data_dir: Path = constants.DEFAULT_DATA_DIR) -> PlaylistSummary:
    """Retrieve the playlist summary of a given playlist.

    If the playlist is not available in the cache, the API will be called.

    Args:
        playlist_name: Name of the playlist to fetch
        data_dir: Path to the cache

    Returns:
        An instantiated summary
    """
    playlist_data_path = data_dir / f"{playlist_name}.json"
    if playlist_data_path.exists():
        return PlaylistSummary(**json.load(open(playlist_data_path, "rb")))
    playlist = get_named_playlist(playlist_name)
    summary = summarize_playlist(playlist)
    with open(playlist_data_path, "w") as _file:
        _file.write(summary.model_dump_json())
    return summary


st.set_page_config(layout="wide")
st.header("Describe playlists")

try:
    playlists = [playlist.name for playlist in get_user_playlists()]
except (HTTPError, ConnectionError):
    playlists = [item.stem for item in list(constants.DEFAULT_DATA_DIR.glob("*.json"))]
    st.warning("⚠️ Unable to reach Spotify. Some playlist may not be found.")

playlist_name = st.selectbox(label="Choose a playlist to describe", options=playlists, index=None)

if playlist_name:
    st.markdown(f"## {playlist_name}")

    playlist = get_playlist(playlist_name)

    tiles = [col.container(height=120, border=True) for col in st.columns(3)]
    _get_nb_tracks_widget(tiles[0], playlist)
    _get_nb_artists_widget(tiles[1], playlist)
    _get_top_artist_widget(tiles[2], playlist)

    tiles = [col.container(height=240, border=True) for col in st.columns([0.3, 0.7])]
    feature_name = tiles[0].selectbox(
        label="Feature", options=list(map(lambda x: x.value, TrackFeature._member_map_.values()))
    )
    _get_average_feature_widget(tiles[0], playlist, feature_name=feature_name)
    _get_distribution_feature_widget(tiles[1], playlist, feature_name)

    _get_dataframe_widget(playlist)
    _download_playlist_widget(playlist)
