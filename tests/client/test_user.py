from unittest.mock import patch

from chopin.client.endpoints import get_likes
from chopin.schemas.track import TrackData


def test_get_likes(spotify_track):
    response = {"items": [{"track": spotify_track}]}
    with patch("chopin.client.playback._client.current_user_saved_tracks", return_value=response):
        liked_tracks = get_likes()
    assert liked_tracks
    assert isinstance(liked_tracks[0], TrackData)
