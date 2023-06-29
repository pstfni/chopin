from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Header, Footer, Static, Button

from chopin.managers.client import ClientManager
from chopin.managers.spotify_client import SpotifyClient

from app import Information, Recommend, Queue, Compose

CLIENT = ClientManager(SpotifyClient().get_client())


class HomePage(App):
    """Homepage for the services."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit Chopin"),
        ("?", "help", "Show help screen"),
    ]
    TITLE = "Chopin"
    CSS_PATH = "css/chopin-app.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(
            Static("Chopin menu", classes="header"),
            Button("Information", id="info", variant="success"),
            Button(
                "Compose a playlist from sources",
                id="compose",
                variant="success",
            ),
            Button(
                "Recommend songs in a new playlist",
                id="recommend",
                variant="success",
            ),
            Button(
                "Create a playlist from the queue",
                id="queue",
                variant="success",
            ),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        match event.button.id:
            case "info":
                self.action_information()
            case "compose":
                self.action_compose()
            case "recommend":
                self.action_recommend()
            case "queue":
                self.action_queue()
        if event.button.id == "start":
            self.add_class("started")
        elif event.button.id == "stop":
            self.remove_class("started")

    def action_information(self):
        self.push_screen(Information(client=CLIENT))

    def action_recommend(self):
        self.push_screen(Recommend(client=CLIENT))

    def action_queue(self):
        self.push_screen(Queue(client=CLIENT))

    def action_compose(self):
        self.push_screen(Compose(client=CLIENT))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """An action to quit the app."""
        self.exit()

    def action_help(self) -> None:
        """An action to show the help screen."""
        # todo : screen with self.__doc__
        pass


if __name__ == "__main__":
    app = HomePage()
    app.run()
