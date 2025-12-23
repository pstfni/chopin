"""Streamlit application.

TODOS ideas:
 Protected playlists
 Queue ---> Show the # of songs in the queue (~10sec refresh)
        --> Button is forbidden if itsn't playing (~10sec refresh)
 Shuffle --> Multiselect (without protected playlists)
 Compose --> Dedicated page (or not ??)
 Compose (with preselected configurations) :
    - new releases
    - recently added to playlists.
    - feeling lucky :sparkles:
"""



from collections.abc import Iterable

import streamlit as st
from buttons import ENTRYPOINTS

st.set_page_config(layout="centered")
st.subheader("Create your ideal playlist from scratch", divider="green")
if st.button(
    label="compose",
    key="compose",
    help="Compose a playlist from various_sources",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/compose.py")

st.subheader("Create simple playlists", divider="green")
columns: Iterable[st.columns] = st.columns(len(ENTRYPOINTS))
for index, column in enumerate(columns):
    with column:
        entrypoint = ENTRYPOINTS[index]
        st.button(
            label=entrypoint.name,
            key=f"button_{entrypoint.name}",
            help=entrypoint.docstring,
            on_click=entrypoint.on_click,
            type="primary",
            use_container_width=True,
        )
