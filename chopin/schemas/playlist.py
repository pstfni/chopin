"""Pydantic schemas for playlists."""

import numpy as np
import pandas as pd
from pydantic import BaseModel, model_serializer, model_validator

from chopin import VERSION
from chopin.schemas.track import TrackData, TrackFeaturesData


class PlaylistData(BaseModel):
    """Playlist representation.

    Attributes:
        name: Name of the playlist
        uri: Spotify URI for the playlist
    """

    name: str
    uri: str
    description: str = ""


class PlaylistSummary(BaseModel):
    """Representation of a full playlist. It is used to describe playlists and back them up.

    Attributes:
        playlist: The playlist described
        tracks: A list of TrackData in the playlist
        _nb_tracks: Number of tracks in the playlist
        _total_duration: Length (in milliseconds) of the playlist
        _nb_artists: Number of artists in the playlist
        _avg_features: Average values across the track features
        _avg_popularity: Average popularity of the tracks in the playlist

    !!! note
        The private attributes are automatically computed in a validator.
    """

    playlist: PlaylistData
    tracks: list[TrackData]
    _nb_tracks: int | None = None
    _total_duration: float | None = None
    _nb_artists: int | None = None
    _avg_features: TrackFeaturesData | None = None
    _avg_popularity: float | None = None

    @model_validator(mode="after")
    def fill_fields(cls, values):
        """Compute field values on initialzation."""
        tracks = values.tracks
        values._nb_tracks = len(tracks)
        values._nb_artists = len(np.unique([track.artists[0].name for track in tracks]))
        values._total_duration = sum([track.duration_ms for track in tracks])
        values._avg_popularity = np.mean([track.popularity for track in tracks])

        # yayks
        attributes = list(TrackFeaturesData.model_fields.keys())
        attributes.pop(-1)  # remove analysis_url
        features = np.mean([[getattr(track.features, feat) for feat in attributes] for track in tracks], axis=0)
        values._avg_features = TrackFeaturesData(**{attributes[i]: round(features[i], 3) for i in range(len(features))})
        # skyay
        return values

    def __str__(self):
        """Represent a playlist summary."""
        return (
            f"------ Playlist {self.playlist.name} ------\n"
            f"\t{self._nb_tracks} tracks\n"
            f"\t{self._nb_artists} artists\n"
            f"\t{self._avg_features} average features\n"
        )

    @model_serializer
    def serialize_model(self):
        """Serialize plalist summaries and add version information."""
        return {
            "playlist": self.playlist.model_dump(),
            "tracks": [track.model_dump() for track in self.tracks],
            "version": VERSION,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Write the playlist summary as a dataframe."""
        dataframe = pd.json_normalize(self.model_dump(), "tracks")
        dataframe["artists"] = dataframe["artists"].apply(lambda x: x[0]["name"])
        return dataframe
