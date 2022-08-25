"""Ideas.

streamlit user dashboard
"""

import random
from collections import Counter
from typing import List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from managers.client import SpotifyClient
from managers.recommendation import RecommendationManager
from managers.track import TrackManager
from managers.user import UserManager
from schemas import ArtistData, TrackData, UserData
from utils import flatten_list

ARTISTS_DISPLAY_COLUMNS = ["name", "genres"]
TRACKS_DISPLAY_COLUMNS = ["name", "artists.name", "album.name", "album.release_date", "popularity"]

# 🛂 Clients and managers initialization
client = SpotifyClient().get_client()
user_manager = UserManager(client)
recommendation_manager = RecommendationManager(client)
track_manager = TrackManager(client)

# 💾 Get the data (and cache it)


@st.cache(allow_output_mutation=True)
def load_hot_data() -> Tuple[UserData, List[TrackData], List[ArtistData]]:
    """Load the "hot" data (user, tracks, and artists) that will be used for the streamlit dashboard.

    Returns:
        A tuple: user, track, and artist data
    """
    current_user = user_manager.get_current_user()
    tracks: List[TrackData] = user_manager.get_hot_tracks()
    tracks = track_manager.set_audio_features(tracks)
    artists: List[ArtistData] = user_manager.get_hot_artists()
    return current_user, tracks, artists


@st.cache(allow_output_mutation=True)
def load_top_data() -> Tuple[UserData, List[TrackData], List[ArtistData]]:
    """Load the "top" data (user, tracks and artists."""
    current_user = user_manager.get_current_user()
    tracks: List[TrackData] = user_manager.get_top_tracks()
    tracks = track_manager.set_audio_features(tracks)
    artists: List[ArtistData] = user_manager.get_top_artists()
    return current_user, tracks, artists


# 🎢 Streamlit page
st.set_page_config(layout="wide", page_title="Dashboard", page_icon=":headphone:")
st.title("Spotify User dashboard")
hot_filter = st.sidebar.radio("View statistics and recommendation for hot or top artists", ("Hot", "Top"))
if hot_filter == "Hot":
    username, tracks, artists = load_hot_data()
else:
    username, tracks, artists = load_top_data()

# 🧭 Recommendation
artists_recommendation_seed: List[str] = [artist.id for artist in artists]
artists_recommendation_seed = random.sample(artists_recommendation_seed, 5)
artists_based_recommendations = recommendation_manager.get_recommendations(10, seed_artists=artists_recommendation_seed)

tracks_recommendation_seed: List[str] = [track.id for track in tracks]
tracks_recommendation_seed = random.sample(tracks_recommendation_seed, 5)
tracks_based_recommendations = recommendation_manager.get_recommendations(10, seed_tracks=tracks_recommendation_seed)

genres = flatten_list([artist.genres for artist in artists])
genres_recommendation_seed = [tup[0] for tup in Counter(genres).most_common(5)]
genre_based_recommendations = recommendation_manager.get_recommendations(10, seed_genres=genres_recommendation_seed)


# 🎨 Feature visualization
tsne_features = TrackManager.compute_tsne(tracks)

# 📊 Displaying everything
st.header(f"{hot_filter} tracks")
tracks_df = pd.DataFrame.from_records([track.to_flatten_dict() for track in tracks], columns=TRACKS_DISPLAY_COLUMNS)
st.dataframe(tracks_df.style.bar(subset="popularity", color="#97D5AB"))
st.header(f"{hot_filter} artists")
artists_df = pd.DataFrame.from_records([artist.dict() for artist in artists], columns=ARTISTS_DISPLAY_COLUMNS)
genres_df = pd.DataFrame([pd.Series(x, dtype=str) for x in artists_df.genres])
artists_df = pd.concat([artists_df, genres_df], axis=1).drop("genres", axis=1)
st.dataframe(artists_df)

st.header("Recommendations")
columns = st.columns(3)
recommendations = {
    "Artists": artists_based_recommendations,
    "Tracks": tracks_based_recommendations,
    "Genres": genre_based_recommendations,
}
buttons = [None, None, None]
for i, (key, recommendation_type) in enumerate(recommendations.items()):
    with columns[i]:
        st.subheader(f"{key} based recommendation")
        for reco in recommendation_type:
            st.write(f"{reco.name} - {reco.artists[0].name}")
        buttons[i] = st.button(label="❤", key=key)

if buttons[0]:
    track_manager.save_tracks(artists_based_recommendations)
if buttons[1]:
    track_manager.save_tracks(tracks_based_recommendations)
if buttons[2]:
    track_manager.save_tracks(genre_based_recommendations)


st.header("Audio features visualization")
figure = px.scatter(x=tsne_features[:, 0], y=tsne_features[:, 1], hover_name=[track.name for track in tracks])
figure.update_traces(marker={"size": 15})
figure.update_layout(showlegend=False)
figure.update_xaxes(visible=False)
figure.update_yaxes(visible=False)
st.plotly_chart(figure, use_container_width=True)
