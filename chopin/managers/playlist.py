"""Operations on spotify playlists."""

from pathlib import Path

import spotipy

from chopin.client.artists import get_artist_top_tracks, get_related_artists, get_this_is_playlist, search_artist
from chopin.client.genres import get_genre_mix_playlist
from chopin.client.playback import get_queue
from chopin.client.playlists import (
    add_tracks_to_playlist,
    create_playlist,
    get_named_playlist,
    get_playlist_tracks,
    get_user_playlists,
    replace_tracks_in_playlist,
)
from chopin.client.tracks import get_recommendations
from chopin.client.user import get_top_artists, get_top_tracks
from chopin.constants import constants
from chopin.managers.selection import SelectionMethod, select_tracks
from chopin.managers.track import set_audio_features, shuffle_tracks
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


def summarize_playlist(playlist: PlaylistData) -> PlaylistSummary:
    """From a given playlist, create its summary.

    Summaries are useful to describe and backup playlists. They contain extensive information about tracks,
    features, and can be serialized.

    Args:
        playlist: The playlist to summarize.

    Returns:
        A playlist summary, with extended informations about tracks and statistics.
    """
    tracks = get_playlist_tracks(playlist.uri)
    tracks = set_audio_features(tracks)
    return PlaylistSummary(playlist=playlist, tracks=tracks)


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


def create_playlist_from_recommendations(
    name: str, nb_songs: int, description: str = "Mix generated from recommendations"
) -> PlaylistData:
    """Create a playlist from the user recent's listening history, with recommendations.

    Args:
        name: The name of the playlist
        nb_songs: Number of songs
        description: An optional description

    Returns:
        The created playlist

    Notes:
        Due to Spotify recommendation limits, the playlist cannot have more than 100 songs.
    """
    playlist = create(name, description, overwrite=True)
    nb_songs = min(nb_songs, 100)

    recent_artists = get_top_artists(time_range="short_term", limit=constants.MAX_SEEDS)
    tracks = get_recommendations(
        seed_artists=[artist.id for artist in recent_artists], seed_genres=[], seed_tracks=[], limit=nb_songs // 2
    )

    recent_tracks = get_top_tracks(time_range="short_term", limit=constants.MAX_SEEDS)
    tracks += get_recommendations(
        seed_artists=[],
        seed_genres=[],
        seed_tracks=[track.id for track in recent_tracks],
        limit=nb_songs // 2,
    )
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


def tracks_from_feature_name(
    seeds: list[TrackData], feature_name: str, feature_value: float, nb_tracks: int
) -> list[TrackData]:
    """Get a number of tracks from a recommendation.

    The recommendation will use a set of tracks as a seed and a feature to target.

    Args:
        seeds: Reference tracks for the recommendation
        feature_name: Target feature to use for the recommendation
        feature_value: Value of the target feature
        nb_tracks: Number of tracks to recommend

    Returns:
        A list of recommended track data.
    """
    seed_tracks = [track.id for track in seeds]
    # from "energy" to "feature_energy"
    feature_name = f"feature_{feature_name}"
    tracks = get_recommendations(
        seed_tracks=seed_tracks, limit=nb_tracks, seed_artists=[], seed_genres=[], **{feature_name: feature_value}
    )
    logger.debug(f"Some seeds: {', '.join([t.name for t in seeds[:5]])}")
    logger.debug(f"Some recommended tracks: {', '.join([t.name for t in tracks[:5]])}")
    return tracks


def tracks_from_radio(
    artist_name: str, nb_tracks: int, selection_method: SelectionMethod | None = None
) -> list[TrackData]:
    """Get tracks from an artist radio.

    !!! note
        Unfortunately an artist radio isn't easily available in the Spotify API.
        A "radio" of related tracks is created by picking top tracks of the artist and its related artists.

    Args:
        artist_name: Name of the artist or band to fetch related tracks from
        nb_tracks: Number of tracks to retrieve.
        selection_method: How tracks are chosen from the retrieved tracks.
            See `SelectionMethod` for available methods. If no method is given, the choice will be random.

    Returns:
        A list of track data from the artist radio.
    """
    artist = search_artist(artist_name)
    if not artist:
        logger.warning(f"Couldn't retrieve artist for search {artist_name}")
        return []
    related_artists = get_related_artists(artist, max_related_artists=constants.MAX_RELATED_ARTISTS)
    tracks = []
    for artist in [artist, *related_artists]:
        tracks.extend(get_artist_top_tracks(artist, constants.MAX_TOP_TRACKS_ARTISTS))
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


def tracks_from_genre(
    genre: str,
    nb_tracks: int,
    release_range: ReleaseRange | None = None,
    selection_method: SelectionMethod | None = None,
) -> list[TrackData]:
    """Find "mixes" based on the requested genre, and retrieve tracks from the "mix" playlist.

    Args:
        genre: A musical genre to find (eg: 'bossa nova', 'cold wave', 'folk', ...).
        nb_tracks: Number of tracks to retrieve.
        release_range: An optional datetime range for the tracks to fetch.
        selection_method: How tracks are chosen from the retrieved tracks.
            See `SelectionMethod` for available methods. If no method is given, the choice will be random.


    Returns:
        A list of tracks in the found playlist, as track data.
    """
    playlist = get_genre_mix_playlist(genre)
    if not playlist:
        logger.warning(f"Couldn't find a playlist for genre {genre}")
        return []
    tracks = get_playlist_tracks(playlist_uri=playlist.uri, release_date_range=release_range)
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
