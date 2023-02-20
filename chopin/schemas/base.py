from datetime import datetime
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, root_validator, validator

from chopin.utils import flatten_dict


class PlaylistData(BaseModel):
    """Playlist representation.

    Attributes:
        name: Name of the playlist
        uri: Spotify URI for the playlist
    """

    name: str
    uri: str


class UserData(BaseModel):
    """User representation.

    Attributes:
        name: Name of the user
        id: The user id
        uri: Spotify URI for the user
    """

    name: str
    id: str
    uri: str


class TrackFeaturesData(BaseModel):
    """Track audio features representation.

    Attributes:
        acousticness: A [0., 1.] value indicating how acoustic the track is. 1 is most acoustic
        danceability: A [0., 1.] value for how suitable the track is for dancing. 1 is most danceable
        energy: A [0., 1.] measure of intensity and activity. 1 feel fast, loud and noisy
        instrumentalness: A [0., 1.] value indicating if the track contains vocals. 1 means no vocal content
        liveness: A [0., 1.] confidence score for whether the track was captured in a live setting. 1 is performed live.
        loudness: A decibel value for how loud the track is. Typically range between -60 and 0db for the loudest tracks.
        speechiness: A [0., 1.] measure for spoken words presence in a track. 1 is a talk show
        valence: A [0., 1.] score for the "positiveness" conveyed by the track. 1 are joyful songs.
        tempo: Beats per minute of a track.
        mode: Track modality. 0 is minor, 1 is major.
        key: Pitch Class Notation for the track key. -1 indicates that no key was detected.
        analysis_url: URL for the spotify page of the audio feature analysis.
    """

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
    """Album data representation.

    Attributes:
        name: Album name
        id: Album id
        uri: Spotify URI for the album
        release_date: The year the album was released.
    """

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
    """Artist data representation.

    Attributes:
        name: Name of the artist
        id: Id of the artist
        uri: Spotify URI for the artist
        genres: A list of strings describing the artist genres

    !!! warning
        The 'genres' information is not always available. And it can be quite flaky
    """

    name: str
    id: str
    uri: str
    genres: Optional[List[str]]

    class Config:
        extra = "ignore"


class TrackData(BaseModel):
    """Representation of a track.

    Attributes:
        name: Track name
        id: Track id
        uri: Spotify URI for the track
        duration_ms: Duration of the track, in milliseconds
        popularity: A [0, 100] measure for the track popularity. 100 is most popular
        album: The album data
        artists: The artists on the track
        features: Audio features of the track.

    !!! warning
        By default, tracks sent by the Spotify API do not contain audio feature information.
        A call to the dedicated endpoint is necessary to fill the attribute.
    """

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
