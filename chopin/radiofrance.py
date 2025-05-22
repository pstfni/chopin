"""Interact with the Radio France API and retrieve webradios queues."""

from enum import Enum, auto

from pydantic import BaseModel, computed_field
from requests import request

BASE_URL = "https://www.radiofrance.fr/"
# https://www.radiofrance.fr/fip/radio-groove/api/songs?pageCursor=Mg%3D%3D


class Brands(str, Enum):
    """Available brands (radios) for Radio France."""

    FIP: auto
    FRANCE_INTER: auto
    FRANCE_MUSIQUE: auto
    FRANCE_CULTURE: auto
    MOUV: auto


class Station(str, Enum):
    """NotImplemented.

    TODO :Implement the station logic: Each brand has a distinct list of
    available stations.     It should be straightforward for users in
    the app or the cli to get available brands and station.
    """


class RadioFranceLinkLabels(str, Enum):
    """Available third party apps in the RadioFrance API response model."""

    spotify = "spotify"
    itunes = "itunes"
    deezer = "deezer"


class RadioFranceLink(BaseModel):
    """Model for RadioFrance song links."""

    label: RadioFranceLinkLabels
    url: str


class RadioFranceSong(BaseModel):
    """Minimal model for Radio France API songs, with the id and a link to the spotify track."""

    id: str
    links: list[RadioFranceLink]

    @computed_field
    def spotify_link(self) -> str | None:
        """Link to the song in Spotify."""
        import ipdb

        ipdb.set_trace()
        spotify_item = [item for item in self.links if item.label == RadioFranceLinkLabels.spotify]
        if not spotify_item:
            return None

        return spotify_item[0].url

    @computed_field
    def spotify_uri(self) -> str | None:
        """URI of the song in Spotify."""
        if self.spotify_link is None:
            return None
        return self.spotify_link.split("/")[-1]


class RadioFranceQueue(BaseModel):
    """Response model of the RadioFrance API."""

    songs: list[RadioFranceSong]
    next: str | None


def get_radio_france_queue(nb_songs: int = 9) -> RadioFranceQueue:
    """Get the queue of a Radio France Web Radio.

    Args:
        nb_songs: Number of songs to retrieve in the queue.

    Returns:
        A queue object with the `songs` and their spotify uris.

    !!! note ""
        There is an hardocded limit of 32 songs to fetch from radio france current radio.
    """
    # TODO implement the radio and brand params.
    url = BASE_URL + "fip/radio-groove/api/songs"
    queue = RadioFranceQueue(songs=[], next=None)
    while len(queue.songs) < min(nb_songs, 32):
        response = request("GET", url, params={"pageCursor": queue.next})
        response.raise_for_status()
        paginated_queue = RadioFranceQueue(**response.json())
        queue.songs = queue.songs + paginated_queue.songs
        queue.next = paginated_queue.next
    return queue
