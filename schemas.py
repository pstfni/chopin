from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from utils import flatten_dict


@dataclass
class PlaylistData:
    name: str
    uri: str
    value: Optional[float] = 1


@dataclass
class UserData:
    name: str
    id: str
    uri: str


class TrackFeaturesData(BaseModel):
    acousticness: float
    danceability: float
    energy: float
    instrumentalness: float
    liveness: float
    loudness: float
    speechiness: float
    valence: float
    tempo: float
    mode: int
    key: int
    analysis_url: str

    class Config:
        extra = "ignore"


class AlbumData(BaseModel):
    name: str
    id: str
    uri: str
    release_date: date

    @validator("release_date", pre=True, allow_reuse=True)
    def parse_release_date(cls, v):
        if isinstance(v, str):
            if len(v) == 10:
                format = "%Y-%m-%d"
            elif len(v) == 7:
                format = "%Y-%m"
            else:
                format = "%Y"
            return datetime.strptime(v, format)
        return v

    class Config:
        extra = "ignore"


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

    def to_flatten_dict(self):
        if isinstance(self.artists, list):
            self.artists = self.artists[0]
        return flatten_dict(self.dict())
