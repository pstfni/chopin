from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from chopin.managers.client import ClientManager


class Compose(Screen):
    """Composition app."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, client: ClientManager):
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        yield Header()

        sources = [
            ListItem(Label("Playlists"), name="playlists"),
            ListItem(Label("Artists"), name="artists"),
            ListItem(Label("Radios"), name="radios"),
            ListItem(Label("Features"), name="features"),
            ListItem(Label("History"), name="history"),
            ListItem(Label("Links"), name="uris"),
        ]
        yield ListView(id="sidebar", *sources)
        yield Static("A", id="center")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        center_screen = self.query_one("#center", Static)
        center_screen.update(f"Selected {event.item.name}")
