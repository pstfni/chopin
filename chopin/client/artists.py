"""Spotify artist related API calls."""

import random

from chopin.client.settings import _client
from chopin.constants import constants
from chopin.schemas.artist import ArtistData
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData
from chopin.tools.strings import match_strings


def get_this_is_playlist(artist_name: str) -> PlaylistData | None:
    """Get an artist "This Is ..." playlist.

    !!! note
        It is not search, but a strict match against the artist name.

    Args:
        artist_name: Name of the artist

    Returns:
        If found, the playlist data for "This Is {name}"
    """
    # NOTE : Strict match for 'This Is artist_name' !
    search = f"This Is {artist_name}"
    response = _client.search(q=search, limit=10, type="playlist", market="fr")["playlists"]
    items = response.get("items")
    if not items:
        raise ValueError(f"Couldn't retrieve playlists for query {artist_name}")
    playlist = [playlist for playlist in items if playlist["owner"]["uri"] == constants.SPOTIFY_USER_URI]
    if playlist:
        return PlaylistData(**playlist[0])


def search_artist(artist_name: str) -> ArtistData | None:
    """Search an artist.

    Args:
        artist_name: Name of the artist

    Returns:
        Artist data, if found.
    """
    response = _client.search(q=artist_name, limit=10, type="artist", market="fr")["artists"]
    items = response.get("items")
    matched_artists = [artist for artist in items if match_strings([artist["name"], artist_name])]
    if matched_artists:
        return ArtistData(**matched_artists[0])


def get_artist_top_tracks(artist: ArtistData, max_tracks: int = 20) -> list[TrackData]:
    """Get an artist top tracks.

    Args:
        artist: current artist.
        max_tracks: maximum number of tracks to find.

    Returns:
        A list of track data.
    """
    response = _client.artist_top_tracks(artist_id=artist.id)
    tracks = response["tracks"]
    return [TrackData(**track) for track in random.sample(tracks, min(len(tracks), max_tracks))]
