"""Chopin API."""
from fastapi import FastAPI

from chopin.constants import constants
from chopin.managers.client import ClientManager
from chopin.managers.playlist import PlaylistManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.schemas.base import PlaylistData, UserData

app = FastAPI(
    title="Chopin API",
)
client: ClientManager = ClientManager(SpotifyClient().get_client())


@app.get("/")
def homepage():
    """Homepage route."""
    return {"Welcome to the Chopin API"}


@app.get("/me")
async def me() -> UserData:
    """Information about the current user."""
    return client.get_current_user()


@app.post("/playlists/recommend")
async def recommend() -> PlaylistData:
    """Create a playlist with recommendations."""
    return PlaylistManager(client).create_playlist_from_recommendations(
        name=constants.RECOMMENDED_MIX.name,
        description=constants.RECOMMENDED_MIX.description,
        nb_songs=constants.RECOMMENDED_MIX.nb_songs,
    )


@app.post("/playlists/queue")
async def queue() -> PlaylistData:
    """Create a playlist from the user's queue."""
    return PlaylistManager(client).create_playlist_from_queue(
        name=constants.QUEUED_MIX.name, description=constants.QUEUED_MIX.description
    )


@app.get("playlists/{name}")
async def get_playlist(name) -> PlaylistData:
    """Retrieve a playlist data based on its name."""
    client.get_user_playlists()
