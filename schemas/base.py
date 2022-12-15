from datetime import datetime
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, root_validator, validator

from utils import flatten_dict


class PlaylistData(BaseModel):
    name: str
    uri: str


class UserData(BaseModel):
    name: str
    id: str
    uri: str


class TrackFeaturesData(BaseModel):
    acousticness: Optional[float]
    danceability: Optional[float]
    energy: Optional[float]
    instrumentalness: Optional[float]
    liveness: Optional[float]
    loudness: Optional[float]
    speechiness: Optional[float]
    valence: Optional[float]
    tempo: Optional[float]
    mode: Optional[int]
    key: Optional[int]
    analysis_url: Optional[str]

    class Config:
        extra = "ignore"


class AlbumData(BaseModel):
    name: str
    id: str
    uri: str
    release_date: str

    @validator("release_date", pre=True, allow_reuse=True)
    def parse_release_date(cls, v):
        if isinstance(v, str):
            if len(v) == 10:
                format = "%Y-%m-%d"
            elif len(v) == 7:
                format = "%Y-%m"
            else:
                format = "%Y"
            return datetime.strptime(v, format).year
        return v.year


class ArtistData(BaseModel):
    name: str
    id: str
    uri: str
    genres: Optional[List[str]]

    class Config:
        extra = "ignore"


class TrackData(BaseModel):
    name: str
    id: str
    uri: str
    duration_ms: int
    popularity: int
    album: Optional[AlbumData] = None
    artists: Optional[List[ArtistData]] = None
    features: Optional[TrackFeaturesData] = None

    def to_flatten_dict(self, **kwargs):
        if isinstance(self.artists, list):
            self.artists = self.artists[0]
        return flatten_dict(self.dict(**kwargs))


class PlaylistSummary(BaseModel):
    playlist: PlaylistData
    tracks: List[TrackData]
    _nb_tracks: Optional[int] = None
    _total_duration: Optional[float] = None
    _nb_artists: Optional[int] = None
    _avg_features: Optional[TrackFeaturesData] = None
    _avg_popularity: Optional[int] = None

    @root_validator()
    def fill_fields(cls, values):
        tracks = values["tracks"]
        values["_nb_tracks"] = len(tracks)
        values["_nb_artists"] = len(np.unique([track.artists[0].name for track in tracks]))
        values["_total_duration"] = sum([track.duration_ms for track in tracks])
        values["_avg_popularity"] = np.mean([track.popularity for track in tracks])

        # yayks
        attributes = list(TrackFeaturesData.__fields__.keys())
        attributes.pop(-1)  # remove analysis_url
        features = np.mean([[getattr(track.features, feat) for feat in attributes] for track in tracks], axis=0)
        values["_avg_features"] = TrackFeaturesData(
            **{attributes[i]: round(features[i], 3) for i in range(len(features))}
        )
        # skyay
        return values

    def __str__(self):
        return (
            f"------ Playlist {self.playlist.name} ------\n"
            f"\t{self._nb_tracks} tracks\n"
            f"\t{self._nb_artists} artists\n"
            f"\t{self._avg_features} average features\n"
        )
