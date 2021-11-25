from dataclasses import dataclass
from typing import Optional

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
class TrackFeaturesData:
    acousticness: confloat(gt=0, le=1)
    danceability: confloat(gt=0, le=1)
    energy: confloat(gt=0, le=1)
    instrumentalness: confloat(gt=0, le=1)
    liveness: confloat(gt=0, le=1)
    loudness: confloat(gt=0, le=1)
    speechiness: confloat(gt=0, le=1)
    valence: confloat(gt=0, le=1)
    popularity: int
    tempo: float
    mode: int
    key: int
    analysis_url: str
