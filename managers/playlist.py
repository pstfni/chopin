import json
import random
from pathlib import Path
from typing import List, Optional

import numpy as np
from pydantic.json import pydantic_encoder
from tqdm import tqdm

from managers.client import ClientManager
from schemas.base import PlaylistData, PlaylistSummary, TrackData
from schemas.composer import ComposerConfig
from utils import get_logger, simplify_string

logger = get_logger(__name__)


class PlaylistManager:
    def __init__(self, client: ClientManager):
        """Class to manage all operations related to your playlists. Here you can fill a playlist, replace its tracks,
        compose a playlist ...

        Args:
            client: A ClientManager instance, for all the calls related to the Spotify API.
        """
        self.client = client

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

    def replace(self, uri: str, tracks: List[TrackData]):
        """Replace playlist items with new ones.

        Args:
           uri: uri of the playlist to replace
           tracks: List of track uuids to add to the playlist
        """
        track_ids = list(set([track.id for track in tracks]))
        self.client.replace_tracks_in_playlist(uri, track_ids)

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
        return np.random.choice(tracks, nb_tracks, replace=False)

    def tracks_from_artist_name(self, artist_name: str, nb_tracks: int, title: str) -> List[TrackData]:
        """Get a number of tracks from an artist or band.

        !!! note
            A Spotify search will be queried to find 'This is [artist_name}' playlists and fetch tracks from it.

        Args:
            artist_name: Name of the artist or band to fetch tracks from
            nb_tracks: Number of tracks to retrieve.
            title: The playlist title to match. For example, 'This is Artist' or "Artist Radio'.

        Returns:
            A list of track data from the artists.
        """
        playlist = self.client.get_titled_playlist(title)
        if not playlist:
            logger.warning(f"Couldn't retrieve tracks for artist {artist_name}")
            return []
        tracks = self.client.get_tracks(playlist_uri=playlist.uri)
        return np.random.choice(tracks, nb_tracks, replace=False)

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
        tracks = self.client.get_recommendations(
            seed_tracks=seed_tracks, limit=nb_tracks, seed_artists=[], seed_genres=[], **{feature_name: feature_value}
        )
        return tracks

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
        if composition_config.playlists and not user_playlists:
            # We must have the existing user playlists in order to retrieve the name from the uri.
            raise AttributeError(
                "Missing the user_playlists parameter. It should be passed"
                "to the compose function if user playlists are in the config."
            )
        for playlist in tqdm(composition_config.playlists):
            logger.info(f"Adding {playlist.nb_songs} tracks from playlist {playlist.name}")
            tracks.extend(
                self.tracks_from_playlist_name(
                    playlist_name=playlist.name, nb_tracks=playlist.nb_songs, user_playlists=user_playlists
                )
            )
        for artist in tqdm(composition_config.artists):
            logger.info(f"Adding {artist.nb_songs} tracks for artist {artist.name}")
            playlist_title = f"This is {artist.name}".lower()
            tracks.extend(
                self.tracks_from_artist_name(artist_name=artist.name, nb_tracks=artist.nb_songs, title=playlist_title)
            )
        for feature in composition_config.features:
            logger.info(f"Adding {feature.nb_songs} tracks from recommendations with {feature.name}")
            seed_tracks = np.random.choice(tracks, 5, replace=False)
            recommended_tracks = self.tracks_from_feature_name(
                seeds=seed_tracks,
                feature_name=feature.name,
                feature_value=feature.value,
                nb_tracks=feature.nb_songs,
            )
            tracks.extend(recommended_tracks)
            logger.info(f"Some recommended tracks: {[t.name for t in recommended_tracks[:5]]}")
        for history in composition_config.history:
            logger.info(f"Adding {history.nb_songs} tracks from user {history.time_range} best songs")
            tracks.extend(self.client.get_history_tracks(time_range=history.time_range, limit=history.nb_songs))
        for artist in tqdm(composition_config.radios):
            logger.info(f"Adding {artist.nb_songs} tracks from the radio of artist {artist.name}")
            playlist_title = f"{artist.name} Radio".lower()
            tracks.extend(
                self.tracks_from_artist_name(artist_name=artist.name, nb_tracks=artist.nb_songs, title=playlist_title)
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
