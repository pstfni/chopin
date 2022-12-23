from textual.app import App, ComposeResult, Widget, RenderResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Static
from textual.containers import Container, Vertical
from schemas.base import PlaylistSummary
from pathlib import Path

class TestApp(App):
    """
    todo: document the test textual app
    """

    BINDINGS = [
        ("k", "toggle_dark", "Toggle Dark Mode"),
        ("q", "quit", "Quit"),
        ("d", "describe", "Describe"),
    ]  # pressing "d" (not ctrl+d) trigger this
    CSS_PATH = "textual_app.css"

    def __init__(self, src_dir: str = "./data/playlists"):
        # should it go here ? I've got no idea 🦧
        super().__init__()
        playlists_paths = list(Path(src_dir).glob("*.json"))
        self.playlists = [PlaylistSummary.parse_file(playlist_path) for playlist_path in playlists_paths]

    def compose(self) -> ComposeResult:
        yield Header()  # app title (class name by default)
        view = ListView(ListItem(Label(self.playlists[0].playlist.name)), id="list-view")
        for playlist in self.playlists[1:]:
            view.append(ListItem(Label(playlist.playlist.name)))
        yield Container(
            view,
            Vertical(Static(id="playlist", expand=True), id="playlist-view"),
        )
        yield Footer()  # bindings display

    def action_toggle_dark_mode(self):
        self.dark = not self.dark

    def action_describe(self):
        pass

    def on_list_view_selected(self, event: ListView.Selected):
        event.stop()
        list_view = self.query_one("#list-view", ListView)
        display = str(self.playlists[list_view.index])

        playlist = self.query_one("#playlist", Static)
        playlist.update(display)
        self.query_one("#playlist-view").scroll_home(animate=False)
        self.sub_title = event.item.name


if __name__ == "__main__":
    app = TestApp()
    app.run()
