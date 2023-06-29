from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, Static

from chopin.managers.client import ClientManager


class Information(Screen):
    """Information screen for the app.

    Renders the current user and the playing track information.
    """

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, client: ClientManager):
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"👋 Hey {self.client.get_current_user().name}")
        currently_playing = self.client.get_currently_playing()
        if currently_playing:
            yield Static(f"🎧 Listening to {currently_playing.name} by {currently_playing.artists[0].name}")
        yield Footer()
