from unittest.mock import patch

import pytest

from chopin.client.endpoints import get_currently_playing, get_queue
from chopin.schemas.track import TrackData


def test_get_currently_playing(spotify_track):
    with patch("chopin.client.endpoints._client.current_playback", return_value={"currently_playing_type": "episode"}):
        track = get_currently_playing()
        assert track is None

    with patch(
        "chopin.client.endpoints._client.current_playback",
        return_value={"item": spotify_track, "currently_playing_type": "track"},
    ):
        track = get_currently_playing()
        assert isinstance(track, TrackData)


def test_get_queue_raise_error():
    with patch("chopin.client.endpoints._client.current_playback", return_value={}), pytest.raises(ValueError):
        get_queue()
