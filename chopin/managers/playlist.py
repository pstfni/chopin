import json
import random
from pathlib import Path
from typing import List, Optional

import numpy as np
import spotipy
from pydantic.json import pydantic_encoder
from tqdm import tqdm

from chopin.managers.client import ClientManager
from chopin.managers.track import TrackManager, find_seeds
from chopin.schemas.base import PlaylistData, PlaylistSummary, TrackData
from chopin.schemas.composer import ComposerConfig
from chopin.utils import get_logger, simplify_string

logger = get_logger(__name__)
MAX_RELATED_ARTISTS = 10
MAX_TOP_TRACKS_ARTISTS = 10


class PlaylistManager:
    def __init__(self, client: ClientManager):
        """Class to manage all operations related to your playlists. Here you can fill a playlist, replace its tracks,
        compose a playlist ...

        Args:
            client: A ClientManager instance, for all the calls related to the Spotify API.
        """
        self.client = client

    def create(self, name: str, description: str = "Randomly Generated Mix", overwrite: bool = True) -> PlaylistData:
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
        user_playlists = self.client.get_user_playlists()
        target_playlist = [playlist for playlist in user_playlists if playlist.name == simplify_string(name)]
        if target_playlist and overwrite:
            self.client.replace_tracks_in_playlist(target_playlist[0].uri, [])
            return target_playlist[0]
        return self.client.create_playlist(name=name, description=description)

    def fill(self, uri: str, tracks: List[TrackData]):
        """Fill a playlist with tracks.

        !!! note
            Duplicate tracks will be removed.

        Args:
            uri: uri of the playlist to fill
            tracks: List of track uuids to add to the playlist
        """
        track_ids = list(set([track.id for track in tracks]))
        self.client.add_tracks_to_playlist(uri, track_ids)

    def create_playlist_from_queue(self, name: str, description: str = "Mix generated from queue") -> PlaylistData:
        """Create a playlist from the user's queue.

        Args:
            name: The name of the playlist
            description: An optional description

        Returns:
            The created playlist

        Notes:
            Due to Spotify limitations, only 20 songs from the queue can be fetched and added to the playlist.
        """
        playlist = self.create(name, description, overwrite=True)
        tracks = self.client.get_queue()
        self.fill(uri=playlist.uri, tracks=tracks)
        return playlist

    def tracks_from_playlist_name(
        self, playlist_name: str, nb_tracks: int, user_playlists: List[PlaylistData]
    ) -> List[TrackData]:
        """Get a number of tracks from a playlist.

        Args:
            playlist_name: The name of your playlist
            nb_tracks: Number of tracks to retrieve
            user_playlists: List of existing user playlists. Used to map the name with the URI.

        Returns:
            A list of track data from the playlists
        """
        playlist = [
            playlist for playlist in user_playlists if simplify_string(playlist_name) == simplify_string(playlist.name)
        ]
        if not playlist:
            logger.warning(f"Couldn't retrieve tracks for playlist {playlist_name}")
            return []
        tracks = self.client.get_tracks(playlist_uri=playlist[0].uri)
        return np.random.choice(tracks, min(nb_tracks, len(tracks)), replace=False)

    def tracks_from_artist_name(self, artist_name: str, nb_tracks: int) -> List[TrackData]:
        """Get a number of tracks from an artist or band.

        !!! note
            A Spotify search will be queried to find 'This is [artist_name}' playlists and fetch tracks from it.

        Args:
            artist_name: Name of the artist or band to fetch tracks from
            nb_tracks: Number of tracks to retrieve.

        Returns:
            A list of track data from the artists.
        """
        playlist = self.client.get_this_is_playlist(artist_name)
        if not playlist:
            logger.warning(f"Couldn't retrieve tracks for artist {artist_name}")
            return []
        tracks = self.client.get_tracks(playlist_uri=playlist.uri)
        return np.random.choice(tracks, min(nb_tracks, len(tracks)), replace=False)

    def tracks_from_feature_name(
        self, seeds: List[TrackData], feature_name: str, feature_value: float, nb_tracks: int
    ) -> List[TrackData]:
        """Get a number of tracks from a recommendation. The recommendation will use a set of tracks as a seed and a
        feature to target.

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
        tracks = self.client.get_recommendations(
            seed_tracks=seed_tracks, limit=nb_tracks, seed_artists=[], seed_genres=[], **{feature_name: feature_value}
        )
        logger.critical(f"Some seeds: {', '.join([t.name for t in seeds[:5]])}")
        logger.critical(f"Some recommended tracks: {', '.join([t.name for t in tracks[:5]])}")
        return tracks

    def tracks_from_radio(self, artist_name: str, nb_tracks: int) -> List[TrackData]:
        """Get tracks from an artist radio.

        !!! note
            Unfortunately an artist radio isn't easily available in the Spotify API.
            A "radio" of related tracks is created by picking top tracks of the artist and its related artists.

        Args:
            artist_name: Name of the artist or band to fetch related tracks from
            nb_tracks: Number of tracks to retrieve.

        Returns:
            A list of track data from the artist radio.
        """
        artist = self.client.search_artist(artist_name)
        if not artist:
            logger.warning(f"Couldn't retrieve artist for search {artist_name}")
            return []
        related_artists = self.client.get_related_artists(artist, max_related_artists=MAX_RELATED_ARTISTS)
        tracks = []
        for artist in [artist] + related_artists:
            tracks.extend(self.client.get_artist_top_tracks(artist, MAX_TOP_TRACKS_ARTISTS))
        return np.random.choice(tracks, min(len(tracks), nb_tracks), replace=False)

    def tracks_from_playlist_uri(self, playlist_uri: str, nb_tracks: int) -> List[TrackData]:
        """Get tracks from a playlist URI.

        Args:
            playlist_uri: Name of the artist or band to fetch related tracks from
            nb_tracks: Number of tracks to retrieve.

        Returns:
            A list of track data from the artist radio.
        """
        try:
            tracks = self.client.get_tracks(playlist_uri=playlist_uri)
        except spotipy.SpotifyException:
            logger.warning(f"Couldn't retrieve playlist URI {playlist_uri}")
            return []
        return np.random.choice(tracks, min(len(tracks), nb_tracks), replace=False)

    def compose(
        self, composition_config: ComposerConfig, user_playlists: Optional[List[PlaylistData]] = None
    ) -> List[TrackData]:
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
        tracks: List[TrackData] = []
        for playlist in tqdm(composition_config.playlists):
            logger.info(f"Adding {playlist.nb_songs} tracks from playlist {playlist.name}")
            tracks.extend(
                self.tracks_from_playlist_name(
                    playlist_name=playlist.name, nb_tracks=playlist.nb_songs, user_playlists=user_playlists
                )
            )
        for artist in tqdm(composition_config.artists):
            logger.info(f"Adding {artist.nb_songs} tracks for artist {artist.name}")
            tracks.extend(self.tracks_from_artist_name(artist_name=artist.name, nb_tracks=artist.nb_songs))
        for history in composition_config.history:
            logger.info(f"Adding {history.nb_songs} tracks from user {history.time_range} best songs")
            tracks.extend(self.client.get_history_tracks(time_range=history.time_range, limit=history.nb_songs))
        for radio in composition_config.radios:
            logger.info(f"Adding {radio.nb_songs} tracks with {radio.name} related artists and songs")
            tracks.extend(self.tracks_from_radio(artist_name=radio.name, nb_tracks=radio.nb_songs))
        for uri in composition_config.uris:
            logger.info(f"Adding {uri.nb_songs} tracks from playlist uri {uri.name}")
            tracks.extend(self.tracks_from_playlist_uri(playlist_uri=uri.name, nb_tracks=uri.nb_songs))
        for feature in composition_config.features:
            logger.info(f"Adding {feature.nb_songs} tracks from recommendations with {feature.name}")
            track_manager = TrackManager(self.client)
            tracks = track_manager.set_audio_features(tracks)
            seed_tracks = find_seeds(tracks, feature.name, feature.value)
            tracks.extend(
                self.tracks_from_feature_name(
                    seeds=seed_tracks,
                    feature_name=feature.name,
                    feature_value=feature.value,
                    nb_tracks=feature.nb_songs,
                )
            )
        return random.sample(tracks, len(tracks))

    @staticmethod
    def dump(playlist: PlaylistSummary, filepath: Path):
        """Dump a playlist in a JSON format.

        Args:
            playlist: The playlist to write
            filepath: Target file to receive the dump
        """
        json_str = json.dumps(playlist, default=pydantic_encoder)
        with open(filepath, "w") as f:
            f.write(json_str)
