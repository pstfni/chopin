"""Chopin API."""

from fastapi import FastAPI

from chopin.client.user import get_current_user
from chopin.constants import constants
from chopin.managers.playlist import create_playlist_from_queue, create_playlist_from_recommendations, shuffle_playlist
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.user import UserData

app = FastAPI(
    title="Chopin API",
)


@app.get("/")
def homepage():
    """Homepage route."""
    return {"Welcome to the Chopin API"}


@app.get("/me")
async def me() -> UserData:
    """Information about the current user."""
    return get_current_user()


@app.post("/recommend")
async def recommend() -> PlaylistData:
    """Create a playlist with recommendations."""
    return create_playlist_from_recommendations(
        name=constants.RECOMMENDED_MIX.name,
        description=constants.RECOMMENDED_MIX.description,
        nb_songs=constants.RECOMMENDED_MIX.nb_songs,
    )


@app.post("/queue")
async def queue() -> PlaylistData:
    """Create a playlist from the user's queue."""
    return create_playlist_from_queue(name=constants.QUEUED_MIX.name, description=constants.QUEUED_MIX.description)


@app.post("/shuffle/{name}")
async def shuffle(name: str) -> None:
    """Shuffle a playlist."""
    shuffle_playlist(name=name)
