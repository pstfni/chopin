"""Streamlit page for the composition form and endpoint."""

from datetime import date, datetime

import pandas as pd
import streamlit as st
from conversion import convert_form_configuration
from requests import ConnectionError, HTTPError

from chopin.client.playlists import get_user_playlists
from chopin.managers.composition import compose
from chopin.managers.playlist import create, fill
from chopin.managers.selection import SelectionMethod
from chopin.schemas.composer import ComposerConfig

MIN_DATE: date = date(1960, 1, 1)
MAX_DATE: date = datetime.now().date()
st.set_page_config(layout="centered")


@st.cache_data()
def get_help_for_user_playlists() -> str:
    """If available, create a useful help string with the names of the current user playlist.

    Returns:
        A string listing possible playlists for the composition.
    """
    try:
        playlists = get_user_playlists()
        help_playlist = "Available playlists: " + "\n\t".join([playlist.name for playlist in playlists])
    except (HTTPError, ConnectionError):
        help_playlist = "Add playlists, and strip all non standard characters."
    return help_playlist


def composer_item_form_dataframe(source: str) -> pd.DataFrame:
    """Create an editable dataframe to let the users configure its composition.

    Args:
        source: The selected source for the composition items. 'playlists', for example.

    Returns:
        An editable dataframe, ready to be displayed in the Streamlit app.
    """
    df = pd.DataFrame(columns=["name", "selection_method", "weight"])
    # todo selectbox or textcolumn based on gethelp (see if not too complicated after that)
    df_config = {
        "name": st.column_config.TextColumn(
            f"{source} name", width="large", required=True, help="Pick songs from {source}"
        ),
        "selection_method": st.column_config.SelectboxColumn(
            "Selection Method",
            default=SelectionMethod.RANDOM.value,
            required=False,
            options=list(map(lambda x: x.value, SelectionMethod._member_map_.values())),
        ),
        "weight": st.column_config.NumberColumn("Weight", min_value=0.0, max_value=2.0, default=1.0),
    }
    form = st.data_editor(df, column_config=df_config, num_rows="dynamic", use_container_width=True, hide_index=True)
    return form


composer_config = ComposerConfig.model_construct()  # Hint: no validation is performed.
st.markdown(
    """
    # Compose
    ---------
    Compose your Spotify playlist from various sources. See the [documentation](https://pstfni.github.io/chopin/guide/)
    for a full explanation of how it works.
    """
)

with st.form("composition_form"):
    composer_config.name = st.text_input(
        value="🤖 Musique Automatique",
        label="Choose a name for your playlist",
        max_chars=128,
    )
    composer_config.nb_songs = st.slider(
        "Pick a number of songs to add in your playlist",
        1,
        500,
        value=100,
    )

    st.subheader(
        "Configure your future playlist, from various sources",
    )

    # todo: loop this
    st.write("Add songs from your own playlists ?")
    st.caption(f"_{get_help_for_user_playlists()}_")
    playlist_config = composer_item_form_dataframe("playlists")

    st.write(
        "Add songs from your favourite artists ?",
    )
    st.caption("_Write the name of the artists. For example, 'Bruce Springsteen'_")
    artist_config = composer_item_form_dataframe("artists")

    st.write(
        "Add songs directly from Spotify playlists links",
    )
    st.caption("_Enter the URL of the Spotify playlist of interest. Chopin will randomly pick songs from it_")
    uri_config = composer_item_form_dataframe("uris")

    st.write("Do you want to add songs from your listening history ?")
    history = st.multiselect(
        "How far back should we go ?",
        ["long_term", "medium_term", "short_term"],
    )

    st.write("Add a constraint and pick songs released between 2 dates ?")
    date_input = st.date_input(
        "Select two dates for your range",
        value=(MIN_DATE, MAX_DATE),
        min_value=MIN_DATE,
        max_value=MAX_DATE,
        format="DD/MM/YYYY",
    )
    if date_input[0] != MIN_DATE and date_input[1] != MAX_DATE:
        composer_config.release_range = date_input

    submitted = st.form_submit_button("Compose my playlist")

# This is outside the form
st.divider()
if submitted:
    with st.spinner():
        composer_config = convert_form_configuration(
            composer_config,
            playlist_config=playlist_config,
            artist_config=artist_config,
            uri_config=uri_config,
            history_config=history,
        )
        composer_config = ComposerConfig.model_validate(composer_config)
        tracks = compose(composer_config)
        playlist = create(name=composer_config.name, description=composer_config.description, overwrite=True)
        fill(uri=playlist.uri, tracks=tracks)
        st.success(f"Playlist {composer_config.name} succesfully created! {len(tracks)} tracks added")

st.stop()
