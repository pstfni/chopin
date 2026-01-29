"""Homepage for the chopin app."""

from typing import Any

import streamlit as st

from chopin.cli.from_queue import from_queue
from chopin.client.endpoints import get_queue, get_user_playlists
from chopin.constants import constants
from chopin.managers.composition import compose_playlist
from chopin.managers.playlist import create, doppelganger_playlist, fill, shuffle_playlist
from chopin.managers.selection import SelectionMethod
from chopin.schemas.composer import ComposerConfig, ComposerConfigItem, ComposerConfigListeningHistory


@st.cache_data()
def queue_length() -> int:
    """Get the length of the queue."""
    try:
        queue = get_queue()
    except ValueError:
        return 0
    return len(queue)


def spacing(nb_lines: int = 5):
    """Add space - as streamlit blank lines,  between elements."""
    for _ in range(nb_lines):
        st.write("")


def _compose(composer_config: ComposerConfig):
    tracks = compose_playlist(composer_config)
    playlist = create(name=composer_config.name, description=composer_config.description, overwrite=True)
    fill(uri=playlist.uri, tracks=tracks)
    st.success(f"Playlist {composer_config.name} succesfully created! {len(tracks)} tracks added")


# submit
def _submit(composer_configuration: ComposerConfig) -> ComposerConfig:
    composer_configuration.playlists = [
        ComposerConfigItem(**playlist) for key, playlist in st.session_state.playlists.items()
    ]
    composer_configuration.uris = [ComposerConfigItem(**uri) for key, uri in st.session_state.uris.items()]
    composer_configuration.history = [
        ComposerConfigListeningHistory(**{"time_range": time_range}) for time_range in st.session_state.history
    ]
    st.write(composer_configuration.model_dump())
    ComposerConfig.model_validate(composer_configuration)
    # _compose(composer_configuration)
    return composer_configuration


st.set_page_config(layout="wide")
st.header("🎶 Chopin")

user_playlists = get_user_playlists()
protected_playlists = [playlist for playlist in user_playlists if playlist.id in constants.PROTECTED_PLAYLISTS_ID]
protected_playlists_name = [playlist.name for playlist in protected_playlists]
unprotected_playlists = [playlist for playlist in user_playlists if playlist.id not in constants.PROTECTED_PLAYLISTS_ID]

queue_col, doppel_col, shuffle_col = st.columns(3)

with queue_col:
    songs_in_queue = queue_length()
    st.subheader("🔮 Queue", divider="green", help=f"{songs_in_queue} songs in queue")

    st.badge(f"{songs_in_queue} songs in queue", icon="📜")
    st.write("")

    queue_button = st.button(
        key="queue",
        label="Create playlist from queue",
        help="Create a playlist from the user's queue. Note that Spotify must be active for this to work.",
        type="primary",
        width="stretch",
        disabled=songs_in_queue == 0,
    )

    if queue_button:
        try:
            from_queue()
            st.success("Playlist created from queue")
        except Exception as exc:
            st.error(f"There was an unexpected error: {exc}")

with doppel_col:
    st.subheader("👬 Doppelganger", divider="green", help="Create a similar playlist from an existing one.")
    original_column, new_column = st.columns(2)
    with original_column:
        selected_playlist = st.selectbox(
            label="Select a playlist to shuffle",
            options=[playlist.name for playlist in user_playlists],
            label_visibility="collapsed",
        )
    with new_column:
        new_playlist_name = st.text_input(
            label="Name for the new playlist.",
            value=constants.RECOMMENDED_MIX.name,
            label_visibility="collapsed",
            icon="✏",
        )

    doppel_button = st.button(
        key="doppel",
        label=f"Create {new_playlist_name}, a doppelganger for {selected_playlist}",
        help="Create a doppelganger playlist from an existing one.",
        type="primary",
        width="stretch",
    )

    if doppel_button:
        if new_playlist_name in protected_playlists:
            st.error(f"{new_playlist_name} is a protected playlist name, you cannot overwrite it.")
        try:
            doppelganger_playlist(selected_playlist, new_playlist_name)
            st.success("Playlist successfully created.")
        except Exception as exc:
            st.error(f"There was an unexpected error: {exc}")


with shuffle_col:
    st.subheader(
        "🔀 Shuffle",
        divider="green",
        help="Choose a playlist to shuffle. Some playlists can be protected by the user and won't appear here.",
    )
    selected_playlist = st.selectbox(
        label="Select a playlist to shuffle",
        options=[playlist.name for playlist in unprotected_playlists],
        label_visibility="collapsed",
    )
    shuffle_button = st.button(
        key="shuffle",
        label=f"Shuffle {selected_playlist}",
        help="Shuffle the selected playlist.",
        type="primary",
        width="stretch",
    )

if shuffle_button:
    try:
        shuffle_playlist(selected_playlist)
        st.success("Playlist successfully shuffled.")
    except Exception as exc:
        st.error(f"There was an unexpected error: {exc}")

spacing(8)

st.subheader("🎼 Compose with selected presets", divider="green")
container = st.container(key="compose-presets", border=False, horizontal=True, horizontal_alignment="center")
# musique automatique
container.button(
    key="button-preset-1",
    label="Musique Automatique",
    help="Create a playlist from a mix of your own playlists.",
    type="primary",
    width="stretch",
    on_click=_compose,
    args=(ComposerConfig.parse_yaml("confs/musique_automatique.yaml"),),
)
# new releases
container.button(
    key="button-preset-2",
    label="Musique Neuve",
    help="Create a playlist with recent releases. ",
    type="primary",
    width="stretch",
    on_click=_compose,
    args=(ComposerConfig.parse_yaml("confs/musique_neuve.yaml"),),
)
# recently added
container.button(
    key="button-preset-3",
    label="Musique Recommandée",  # TODO: find a better name
    help="Create a playlist with songs recently added to your playlistss",
    type="primary",
    width="stretch",
    on_click=_compose,
    args=(ComposerConfig.parse_yaml("confs/musique_recommandee.yaml"),),
)


spacing(8)

st.subheader("🎶 Compose your own playlist", divider="green")
# Hint: no validation is performed as we populate the object.
composer_config = ComposerConfig.model_construct()


composer_config.name = st.text_input(
    value="🤖 Musique Automatique", label="Choose a name for your playlist", max_chars=128
)
if composer_config.name in protected_playlists_name:
    st.error(
        f"🛑 {composer_config.name} is a protected playlist, you cannot use it as a name for your new playlist."
        "Otherwise its content will be deleted and replaced with this position"
    )
composer_config.nb_songs = st.slider(
    "Choose a number of songs to add in your playlist",
    1,
    500,
    value=100,
)

st.write("### Add songs from your playlists ? ")
add_from_playlists = st.checkbox(
    "Select songs from your playlists", value=True, help="Toggle to add songs from the user's playlists."
)

if "playlists" not in st.session_state:
    st.session_state.playlists = {}


def _add_playlist(name: str, config: dict[str, Any]) -> None:
    """Add the playlist configuration selected bu the user to the session state, for later use."""
    st.session_state.playlists[name] = config


if add_from_playlists:
    selected_playlists = st.multiselect(
        "Select playlists to include",
        options=[playlist.name for playlist in protected_playlists],
        help="Choose one or more playlists to add songs from",
        key="playlists-multiselect",
    )
    if selected_playlists:
        for playlist_name in selected_playlists:
            container = st.container(
                key=f"container {playlist_name}", border=True, horizontal=True, horizontal_alignment="center"
            )
            container.write(f"### {playlist_name}")
            selection_method = container.selectbox(
                label="Select the method to use to choose songs in the playlist",
                options=[
                    SelectionMethod.RANDOM.value,
                    SelectionMethod.POPULARITY.value,
                    SelectionMethod.LATEST.value,
                    SelectionMethod.ORIGINAL.value,
                ],
                index=0,
                key=f"select-method-{playlist_name}",
                label_visibility="collapsed",
            )
            weight = container.slider(
                f"Weight for {playlist_name}",
                min_value=0.0,
                max_value=2.0,
                value=1.0,
                step=0.1,
                width=128,
                help="Adjust the importance of this playlist in the composition",
                label_visibility="collapsed",
            )
            add_button = container.button(
                key=f"button-{playlist_name}",
                label="Add to composition",
                help=f"Add {playlist_name} configuration to composition",
                type="primary",
                width="stretch",
                on_click=_add_playlist,
                args=(playlist_name, {"name": playlist_name, "weight": weight, "selection_method": selection_method}),
            )
            if add_button:
                print(st.session_state.playlists)
                container.success(f"Playlist {playlist_name} added to composition")

st.write("### Add songs from Spotify URIs ? ")
add_from_uris = st.checkbox(
    "Select songs from Spotify URIs",
    value=False,
    help="Toggle to add songs from public playlists. Note that Spotify owned playlists might be unavailable.",
)

if "containers" not in st.session_state:
    st.session_state.containers = []
if "uris" not in st.session_state:
    st.session_state.uris = {}


def _add_container_uri():
    """Utility function to add a container (row) to the interface."""
    st.session_state.containers.append([])


def _remove_container_uri(index: int):
    """Utility function to remove a container (row) from the interface."""
    st.session_state.containers.pop(index)


def _add_uri(uri, config):
    """Add the uri configuration selected bu the user to the session state, for later use."""
    st.session_state.uris[uri] = config


uri_playlists_config = {}
if add_from_uris:
    new_uri_button = st.button(label="Add new uri", key="new-uri-button", on_click=_add_container_uri)
    for i, _ in enumerate(st.session_state.containers):
        uri_container = st.container(
            key=f"container-uri-{i}", border=True, horizontal=True, horizontal_alignment="center"
        )
        remove_button = uri_container.button(
            key=f"remove-button-{i}",
            label="❌",
            type="tertiary",
            width="content",
            on_click=_remove_container_uri,
            args=(i,),
        )
        uri = uri_container.text_input(label="Enter Spotify URI", key=f"uri-input-{i}", label_visibility="collapsed")
        selection_method = uri_container.selectbox(
            label="Select the method to use to choose songs in the URI",
            options=[
                SelectionMethod.RANDOM.value,
                SelectionMethod.POPULARITY.value,
                SelectionMethod.LATEST.value,
                SelectionMethod.ORIGINAL.value,
            ],
            index=0,
            key=f"select-method-uri-{i}",
            label_visibility="collapsed",
        )
        weight = uri_container.slider(
            "Weight for uri",
            key=f"weight-input-{i}",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            width=128,
            help="Adjust the importance of this playlist in the composition",
            label_visibility="collapsed",
        )
        add_button = uri_container.button(
            key=f"button-{uri}-{i}",
            label="Add to composition",
            help="Add uri configuration to composition",
            type="primary",
            width="stretch",
            on_click=_add_uri,
            args=(uri, {"name": uri, "weight": weight, "selection_method": selection_method}),
        )
        if add_button:
            uri_container.success("Playlist added to composition")

st.write("### Add songs from your listening history ?")
if "history" not in st.session_state:
    st.session_state.history = []
enable_history = st.checkbox(
    "Enable listening history",
    value=False,
    help="Toggle to add songs from your listening history",
)


def _add_history():
    """Add the history configuration selected bu the user to the session state, for later use."""
    if st.session_state.get("time_range_options"):
        st.session_state.history = st.session_state.time_range_options


if enable_history:
    container = st.container(key="container-history", border=True, horizontal=True, horizontal_alignment="center")
    option_map = {
        "short_term": "Short term",
        "medium_term": "Medium term",
        "long_term": "Long Term",
    }

    selected_pills = container.pills(
        "Select time ranges",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        help="Select the time ranges to include in the listening history",
        key="time_range_options",
        selection_mode="multi",
        label_visibility="collapsed",
        on_change=_add_history,
        width="stretch",
    )


st.write("")
st.write("")

submit_button = st.button(
    key="submit",
    label="Submit",
    help="Submit the configuration to create the playlist",
    type="primary",
    width="stretch",
    on_click=_submit,
    args=(composer_config,),
)
clear_button = st.button(
    key="clear",
    label="Clear",
    help="Clear the app",
    type="secondary",
    width="stretch",
)
if clear_button:
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.clear()
    st.rerun()
