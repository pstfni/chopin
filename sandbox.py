from pathlib import Path
from typing import Any, List, Literal
import numpy as np
from collections import Counter
import pandas as pd
from utils import get_logger
from ml.data import read_playlist
from datetime import datetime
from pydantic import BaseModel
from schemas import TrackData
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

logger = get_logger(__name__)
TRACK_FEATURES = [
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "speechiness",
    "valence",
]


class PlaylistWithTracks(BaseModel):
    name: str
    tracks: List[TrackData]


def get_last_update(playlists_filepaths: List[Path]) -> str:
    """
    Get the creation time of the playlist JSON file. Used to check the time of the last update.

    Args:
        playlists_filepaths: The paths to the JSON files describing the playlists

    Returns:
        A string representation of the last update timestamp. Format is 'day month hour:minutes"
    """
    return datetime.fromtimestamp(playlists_filepaths[0].lstat().st_ctime).strftime("%d %b %H:%M")


def get_feature_statistic(
    playlist: PlaylistWithTracks, feature: str, statistic: Literal["max", "min", "mean", "std"] = "mean"
) -> float:
    """
    Retrieve the _statistic_ (max, min, mean or standard dev) of a feature in a playlist

    Args:
        playlist: A playlist with its tracks
        feature: The target feature. See schemas.TrackFeaturesData for more information
        statistic: The stat to use for aggregation.

    Returns:
        The statistic value, aggregated over the playlist tracks
    """
    return round(getattr(np, statistic)([getattr(track.features, feature) for track in playlist.tracks]), 3)


def get_duplicates(playlist: PlaylistWithTracks) -> List[str]:
    """
    Get duplicate tracks in a playlist.

    Args:
        playlist: A playlist with its tracks.

    Returns:
        Duplicate track names (if any)

    """
    items_count = Counter([track.id for track in playlist.tracks])
    duplicates_indexes = [ind for ind, tcount in enumerate(items_count.values()) if tcount > 1]
    return [playlist.tracks[ind].name for ind in duplicates_indexes]


# 💾 Data
playlist_filepaths: List[Path] = list(Path("data/playlists/").glob("*.json"))
playlists = [
    PlaylistWithTracks(name=playlist[0], tracks=playlist[1])
    for playlist in [read_playlist(playlist_path) for playlist_path in playlist_filepaths]
]


# 🎢 Streamlit page
st.set_page_config(layout="wide", page_title="Playlists Dashboard", page_icon=":folder:")
st.title("Spotify Playlist dashboard")
st.header("Overall information")
if not playlists:
    st.warning(
        "No playlists were found locally. To use the dashboard, please _describe_ your playlists first", icon="⚠"
    )
columns = st.columns(3)
columns[0].metric("Number of playlists", value=len(playlists))
columns[1].metric("Total number of songs", value=sum([len(p.tracks) for p in playlists]))
columns[2].metric("Last update", value=get_last_update(playlist_filepaths))
if columns[2].button(label="Update"):
    pass  # todo -> implement description here

playlists_statistics: List[List[Any]] = []
for playlist in playlists:
    avg_features = [get_feature_statistic(playlist, statistic="mean", feature=feature) for feature in TRACK_FEATURES]
    playlists_statistics.append([playlist.name, len(playlist.tracks), *avg_features])
display_df = pd.DataFrame(playlists_statistics, columns=["name", "tracks", *TRACK_FEATURES])

st.header("Playlist statistics")
st.dataframe(display_df.style.format({name: "{:.3}" for name in TRACK_FEATURES}), use_container_width=True)

st.header("Playlist features visualization")
n_columns = 4
columns = st.columns(n_columns)
df_columns_features = [display_df.columns.get_loc(c) for c in TRACK_FEATURES]
for display_rows in range(0, len(playlists), n_columns):
    for c, row_index in enumerate(range(display_rows, display_rows + n_columns)):
        columns[c].write(display_df.iloc[row_index, 0])
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=[display_df.iloc[row_index, i] for i in df_columns_features],
                theta=TRACK_FEATURES,
                fill="toself",
                name=display_df.iloc[row_index, 0],
            )
        )
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])), showlegend=False)
        columns[c].plotly_chart(fig, use_container_width=True)

# single playlist page
# print(get_duplicates(playlists[3]))
# tsne = TrackManager.compute_tsne(playlists[1].tracks)
# fig = px.scatter(x=tsne[:, 0], y=tsne[:, 1], hover_name=[track.name for track in playlists[1].tracks])
# fig.show()
# recommendations based on the playlist
