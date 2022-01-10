from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, validator


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
    uri: str
    release_date: date

    @validator("release_date", pre=True)
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
    uri: str

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
