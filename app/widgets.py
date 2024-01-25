"""Widgets for pages of the app."""
from collections import Counter

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from chopin.schemas.playlist import PlaylistSummary


def _get_nb_tracks_widget(container: st.container, playlist: PlaylistSummary) -> None:
    container.metric(label="Number of songs", value=playlist._nb_tracks)


def _get_nb_artists_widget(container: st.container, playlist: PlaylistSummary) -> None:
    container.metric(label="Number of artists", value=playlist._nb_artists)


def _get_top_artist_widget(container: st.container, playlist: PlaylistSummary) -> None:
    artists = [track.artists[0].name for track in playlist.tracks]
    top_artist = Counter(artists).most_common(1)[0]
    container.metric(label="Most represented artist", value=f"{top_artist[0]} ({top_artist[1]})")


def _get_average_feature_widget(container: st.container, playlist: PlaylistSummary, feature_name: str) -> None:
    container.metric(label=f"Average {feature_name}", value=getattr(playlist._avg_features, feature_name))


def _get_distribution_feature_widget(container: st.container, playlist: PlaylistSummary, feature_name: str) -> None:
    values = [getattr(track.features, feature_name) for track in playlist.tracks]
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=values,
            y=np.zeros(len(values)),
            name="acousticness",
            mode="markers",
            marker=dict(
                size=40,
                symbol="line-ns",
                line=dict(width=4, color=values),
            ),
        )
    )
    figure.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        colorscale=dict(sequential=px.colors.get_colorscale("plasma")),
        height=224,
    )
    container.plotly_chart(
        figure,
        use_container_width=True,
        height=224,
        config={"displayModeBar": False},
    )


def _get_dataframe_widget(playlist: PlaylistSummary) -> None:
    playlist_as_df = playlist.to_dataframe()
    playlist_as_df = playlist_as_df.drop(labels=["id", "uri", "album.id", "album.uri", "features.analysis_url"], axis=1)
    st.dataframe(data=playlist_as_df, hide_index=True, use_container_width=True)


def _download_playlist_widget(playlist: PlaylistSummary) -> None:
    columns = st.columns(6)
    columns[5].download_button(
        label="Download playlist", file_name=f"data/{playlist.playlist.name}.json", data=playlist.model_dump_json()
    )
