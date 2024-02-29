from chopin.client.user import get_top_tracks
from chopin.managers.playlist import (
    logger,
    tracks_from_artist_name,
    tracks_from_feature_name,
    tracks_from_genre,
    tracks_from_playlist_name,
    tracks_from_playlist_uri,
    tracks_from_radio,
)
from chopin.managers.track import find_seeds, set_audio_features
from chopin.schemas.composer import ComposerConfig
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData


from tqdm import tqdm


import random


def compose(composition_config: ComposerConfig, user_playlists: list[PlaylistData] | None = None) -> list[TrackData]:
    """From a composition configuration, compose a playlist.

    Args:
        composition_config: A configuration, with playlists, artists, and/or features
            that should be used to create the playlist.
        user_playlists: Existing playlists for the user. Used to map the name of the playlist in
            the configuration with the Spotify URI.

    Returns:
        A list of track data, the tracks to be added to your playlist. The tracks are shuffled.

    Raises:
        AttributeError: if 'playlists' are in the configuration but user_playlists is not passed.
    """
    tracks: list[TrackData] = []
    for playlist in tqdm(composition_config.playlists):
        logger.info(f"Adding {playlist.nb_songs} tracks from playlist {playlist.name}")
        tracks.extend(
            tracks_from_playlist_name(
                playlist_name=playlist.name,
                nb_tracks=playlist.nb_songs,
                user_playlists=user_playlists,
                release_range=composition_config.release_range,
            )
        )
    for artist in tqdm(composition_config.artists):
        logger.info(f"Adding {artist.nb_songs} tracks for artist {artist.name}")
        tracks.extend(
            tracks_from_artist_name(
                artist_name=artist.name, nb_tracks=artist.nb_songs, release_range=composition_config.release_range
            )
        )
    for history in composition_config.history:
        logger.info(f"Adding {history.nb_songs} tracks from user {history.time_range} best songs")
        tracks.extend(get_top_tracks(time_range=history.time_range, limit=history.nb_songs))
    for radio in composition_config.radios:
        logger.info(f"Adding {radio.nb_songs} tracks with {radio.name} related artists and songs")
        tracks.extend(tracks_from_radio(artist_name=radio.name, nb_tracks=radio.nb_songs))
    for uri in composition_config.uris:
        logger.info(f"Adding {uri.nb_songs} tracks from playlist uri {uri.name}")
        tracks.extend(
            tracks_from_playlist_uri(
                playlist_uri=uri.name, nb_tracks=uri.nb_songs, release_range=composition_config.release_range
            )
        )
    for genre in composition_config.genres:
        logger.info(f"Adding {genre.nb_songs} tracks from genre {genre.name}")
        tracks.extend(
            tracks_from_genre(
                genre=genre.name, nb_tracks=genre.nb_songs, release_range=composition_config.release_range
            )
        )
    for feature in composition_config.features:
        logger.info(f"Adding {feature.nb_songs} tracks from recommendations with {feature.name}")
        tracks = set_audio_features(tracks)
        seed_tracks = find_seeds(tracks, feature.name, feature.value)
        tracks.extend(
            tracks_from_feature_name(
                seeds=seed_tracks,
                feature_name=feature.name,
                feature_value=feature.value,
                nb_tracks=feature.nb_songs,
            )
        )
    return random.sample(tracks, len(tracks))
