from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, Static

from app.names import RECOMMENDED_MIX
from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager


class Recommend(Screen):
    """Success (or failure) screen to create a playlist from the user recent listening habits."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, client: ClientManager):
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        yield Header()
        try:
            playlist = PlaylistManager(self.client).create_playlist_from_recommendations(
                name=RECOMMENDED_MIX, nb_songs=100
            )
            yield Static(f"Queued playlist successfully created: {playlist.name}")
        except ValueError as e:
            yield Static(f"Couldn't create the queued playlist: {e}")
        yield Footer()
