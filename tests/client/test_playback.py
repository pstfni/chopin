from unittest.mock import ANY, Mock, patch

import pytest

from chopin.client.playback import get_currently_playing, get_queue
from chopin.schemas.track import TrackData


def test_get_currently_playing(spotify_track):
    with patch("chopin.client.playback._client.current_playback", return_value={"currently_playing_type": "episode"}):
        track = get_currently_playing()
        assert track is None

    with patch(
        "chopin.client.playback._client.current_playback",
        return_value={"item": spotify_track, "currently_playing_type": "track"},
    ):
        track = get_currently_playing()
        assert isinstance(track, TrackData)


def test_get_queue_raise_error():
    with patch("chopin.client.playback._client.current_playback", return_value={}), pytest.raises(ValueError):
        get_queue()


def test_get_queue(spotify_track):
    response = Mock(json=Mock(return_value={"queue": [spotify_track]}), raise_for_status=Mock())
    with patch(
        "chopin.client.playback._client.current_playback", return_value={"is_playing": True}
    ) as _playback, patch("chopin.client.playback._client.auth_manager.get_access_token", return_value=""):
        with patch("chopin.client.playback._client._session.request", return_value=response) as mock_request:
            _ = get_queue()
    mock_request.assert_called_once_with(
        method="GET", url="https://api.spotify.com/v1/me/player/queue", headers=ANY, timeout=5, proxies=None
    )
