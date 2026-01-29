"""Pydantic schemas for playlists."""

from pydantic import BaseModel, model_serializer, model_validator

from chopin import VERSION
from chopin.schemas.track import TrackData


class PlaylistData(BaseModel):
    """Playlist representation.

    Attributes:
        name: Name of the playlist
        uri: Spotify URI for the playlist
    """

    name: str
    uri: str
    id: str
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
    _avg_popularity: float | None = None

    @model_validator(mode="after")
    def fill_fields(self):
        """Compute field values on initialzation."""
        tracks = self.tracks
        popularities = [track.popularity for track in tracks]
        self._nb_tracks = len(tracks)
        self._nb_artists = len(set(track.artists[0].name for track in tracks))
        self._total_duration = sum([track.duration_ms for track in tracks])
        self._avg_popularity = sum(popularities) / len(popularities) if popularities else 0
        return self

    def __str__(self):
        """Represent a playlist summary."""
        return (
            f"------ Playlist {self.playlist.name} ------\n\t{self._nb_tracks} tracks\n\t{self._nb_artists} artists\n"
        )

    @model_serializer
    def serialize_model(self):
        """Serialize plalist summaries and add version information."""
        return {
            "playlist": self.playlist.model_dump(),
            "tracks": [track.model_dump() for track in self.tracks],
            "version": VERSION,
        }
