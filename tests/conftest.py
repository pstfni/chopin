import pytest

from schemas import PlaylistData, TrackData


def track_data(id_: str = "id") -> TrackData:
    """
    Helper to create tracks.
    Args:
        id_: Argument to generate the id. Useful to make sure unique tracks can be created across a test.

    Returns:
        A track, schematized as a TrackData
    """
    return TrackData(
        name=f"test_track_{id_}",
        id=f"{id_}",
        uri=f"spotify:track:{id_}",
        duration_ms=1000,
        popularity=50,
    )


@pytest.fixture
def playlist_1_tracks():
    return [track_data(id_=f"p_{i}") for i in range(50)]


@pytest.fixture
def playlist_2_tracks():
    return [track_data(id_=f"q_{i}") for i in range(25)]


@pytest.fixture
def empty_playlist():
    return []


@pytest.fixture
def playlist_1():
    return PlaylistData(name="p", id="id_p", uri="spotify:playlist:id_p")


@pytest.fixture
def playlist_2():
    return PlaylistData(name="q", id="id_q", uri="spotify:playlist:id_q")


@pytest.fixture
def audio_feature():
    return {
        "acousticness": 0.00242,
        "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B\n",
        "danceability": 0.585,
        "duration_ms": 237040,
        "energy": 0.842,
        "id": "2takcwOaAZWiXQijPHIx7B",
        "instrumentalness": 0.00686,
        "key": 9,
        "liveness": 0.0866,
        "loudness": -5.883,
        "mode": 0,
        "speechiness": 0.0556,
        "tempo": 118.211,
        "time_signature": 4,
        "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B\n",
        "type": "audio_features",
        "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
        "valence": 0.428,
    }
