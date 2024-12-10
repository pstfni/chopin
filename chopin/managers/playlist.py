"""Operations on spotify playlists."""

from pathlib import Path

import spotipy

from chopin.client.artists import get_this_is_playlist
from chopin.client.playback import get_queue
from chopin.client.playlists import (
    add_tracks_to_playlist,
    create_playlist,
    get_named_playlist,
    get_playlist_tracks,
    get_user_playlists,
    replace_tracks_in_playlist,
)
from chopin.managers.selection import SelectionMethod, select_tracks
from chopin.managers.track import shuffle_tracks
from chopin.schemas.playlist import PlaylistData, PlaylistSummary
from chopin.schemas.track import TrackData
from chopin.tools.dates import ReleaseRange
from chopin.tools.logger import get_logger
from chopin.tools.strings import simplify_string

logger = get_logger(__name__)


def create(name: str, description: str = "Randomly Generated Mix", overwrite: bool = True) -> PlaylistData:
    """Create a new, empty, playlist.

    !!! warning
        If the `name` of the playlist is an existing playlist, and overwrite is `True`, the said playlist will
        be emptied.

    Args:
        name: name of your playlist.
        description: description of your playlist
        overwrite: Overwrite the existing playlist if the `name` is already used.

    Returns:
        Created playlist
    """
    user_playlists = get_user_playlists()
    target_playlist = [playlist for playlist in user_playlists if playlist.name == simplify_string(name)]
    if target_playlist:
        if overwrite:
            replace_tracks_in_playlist(target_playlist[0].uri, [])
            return target_playlist[0]
        else:
            raise ValueError(
                f"Trying to create a playlist {name} but there is already such a playlist."
                "Use `overwrite=True` if you want to erase the playlist."
            )
    return create_playlist(name=name, description=description)


def fill(uri: str, tracks: list[TrackData]):
    """Fill a playlist with tracks.

    !!! note
        Duplicate tracks will be removed.

    Args:
        uri: uri of the playlist to fill
        tracks: List of track uuids to add to the playlist
    """
    track_ids = list(set([track.id for track in tracks]))
    add_tracks_to_playlist(uri, track_ids)


def shuffle_playlist(name: str) -> PlaylistData:
    """Fetch a playlist from its name and shuffle_playlist it.

    Args:
        name: playlist name.

    Returns:
        Shuffled playlist data.

    Raises:
        ValueError: If the playlist name was not found.
    """
    playlist = get_named_playlist(name)
    if not playlist:
        raise ValueError(f"Playlist {name} not found.")

    tracks = get_playlist_tracks(playlist.uri)
    tracks = shuffle_tracks(tracks)
    replace_tracks_in_playlist(playlist.uri, track_ids=[track.id for track in tracks])
    return playlist


def create_playlist_from_queue(name: str, description: str = "Mix generated from queue") -> PlaylistData:
    """Create a playlist from the user's queue.

    Args:
        name: The name of the playlist
        description: An optional description

    Returns:
        The created playlist

    Notes:
        Due to Spotify limitations, only 20 songs from the queue can be fetched and added to the playlist.
    """
    playlist = create(name, description, overwrite=True)
    tracks = get_queue()
    fill(uri=playlist.uri, tracks=tracks)
    return playlist


def tracks_from_artist_name(
    artist_name: str,
    nb_tracks: int,
    release_range: ReleaseRange | None = None,
    selection_method: SelectionMethod | None = None,
) -> list[TrackData]:
    """Get a number of tracks from an artist or band.

    !!! note
        A Spotify search will be queried to find 'This is [artist_name}' playlists and fetch tracks from it.

    Args:
        artist_name: Name of the artist or band to fetch tracks from
        nb_tracks: Number of tracks to retrieve.
        release_range: An optional datetime range for the release date of the tracks.
        selection_method: How tracks are chosen from the retrieved tracks.
            See `SelectionMethod` for available methods. If no method is given, the choice will be random.

    Returns:
        A list of track data from the artists.
    """
    playlist = get_this_is_playlist(artist_name)
    if not playlist:
        logger.warning(f"Couldn't retrieve tracks for artist {artist_name}")
        return []
    tracks = get_playlist_tracks(playlist_uri=playlist.uri, release_date_range=release_range)
    return select_tracks(tracks, nb_tracks, selection_method)


def tracks_from_playlist_uri(
    playlist_uri: str,
    nb_tracks: int,
    release_range: ReleaseRange | None = None,
    selection_method: SelectionMethod | None = None,
) -> list[TrackData]:
    """Get tracks from a playlist URI.

    Args:
        playlist_uri: Name of the artist or band to fetch related tracks from
        nb_tracks: Number of tracks to retrieve.
        release_range: An optional datetime range for the release date of the tracks.
        selection_method: How tracks are chosen from the retrieved tracks.
            See `SelectionMethod` for available methods. If no method is given, the choice will be random.

    Returns:
        A list of track data from the artist radio.
    """
    try:
        tracks = get_playlist_tracks(playlist_uri=playlist_uri, release_date_range=release_range)
    except spotipy.SpotifyException:
        logger.warning(f"Couldn't retrieve playlist URI {playlist_uri}")
        return []
    return select_tracks(tracks, nb_tracks, selection_method)


def tracks_from_playlist_name(
    playlist_name: str,
    nb_tracks: int,
    user_playlists: list[PlaylistData],
    release_range: ReleaseRange | None = None,
    selection_method: SelectionMethod | None = None,
) -> list[TrackData]:
    """Get a number of tracks from a playlist.

    Args:
        playlist_name: The name of your playlist
        nb_tracks: Number of tracks to retrieve
        user_playlists: List of existing user playlists. Used to map the name with the URI.
        release_range: An optional datetime range for the release date of the tracks.
        selection_method: How tracks are chosen from the retrieved tracks.
            See `SelectionMethod` for available methods. If no method is given, the choice will be random.

    Returns:
        A list of track data from the playlists
    """
    playlist = [
        playlist for playlist in user_playlists if simplify_string(playlist_name) == simplify_string(playlist.name)
    ]
    if not playlist:
        logger.warning(f"Couldn't retrieve tracks for playlist {playlist_name}")
        return []
    tracks = get_playlist_tracks(playlist_uri=playlist[0].uri, release_date_range=release_range)
    return select_tracks(tracks, nb_tracks, selection_method)


def dump(playlist: PlaylistSummary, filepath: Path):
    """Dump a playlist in a JSON format.

    Args:
        playlist: The playlist to write
        filepath: Target file to receive the dump
    """
    json_str = playlist.model_dump_json()
    with open(filepath, "w") as f:
        f.write(json_str)
