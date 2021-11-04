from dataclasses import dataclass
from typing import List, Optional
from pydantic import confloat


@dataclass
class PlaylistData:
    name: str
    uri: str
    value: Optional[confloat(gt=0, le=1)] = 1


@dataclass
class UserData:
    name: str
    id: str
    uri: str


@dataclass
class ArtistData:
    name: str
    id: str
    uri: str


@dataclass
class TrackFeaturesData:
    acousticness: confloat(gt=0, le=1)
    danceability: confloat(gt=0, le=1)
    energy: confloat(gt=0, le=1)
    instrumentalness: confloat(gt=0, le=1)
    liveness: confloat(gt=0, le=1)
    loudness: float
    speechiness: confloat(gt=0, le=1)
    valence: confloat(gt=0, le=1)
    popularity: int
    tempo: float
    mode: int
    key: int
    analysis_url: str


@dataclass
class TrackData:
    name: str
    uri: str
    popularity: int
    id: str
    artist: List[ArtistData]
    features: Optional[TrackFeaturesData]
