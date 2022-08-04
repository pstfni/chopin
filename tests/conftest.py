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


# Fixtures for values expected to be returned by the Spotify API.
# Taken straight from their documentation https://developer.spotify.com/documentation/web-api/reference
@pytest.fixture
def spotify_audio_feature():
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


@pytest.fixture
def spotify_playlist():
    return {
        "collaborative": True,
        "description": "string",
        "external_urls": {"spotify": "string"},
        "followers": {"href": "string", "total": 0},
        "href": "string",
        "id": "string",
        "images": [
            {"url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n", "height": 300, "width": 300}
        ],
        "name": "string",
        "owner": {
            "external_urls": {"spotify": "string"},
            "followers": {"href": "string", "total": 0},
            "href": "string",
            "id": "string",
            "type": "user",
            "uri": "string",
            "display_name": "string",
        },
        "public": True,
        "snapshot_id": "string",
        "tracks": {
            "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20\n",
            "items": [{}],
            "limit": 20,
            "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
            "offset": 0,
            "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
            "total": 4,
        },
        "type": "string",
        "uri": "string",
    }


@pytest.fixture
def spotify_user():
    return {
        "country": "string",
        "display_name": "string",
        "email": "string",
        "explicit_content": {"filter_enabled": True, "filter_locked": True},
        "external_urls": {"spotify": "string"},
        "followers": {"href": "string", "total": 0},
        "href": "string",
        "id": "string",
        "images": [
            {"url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n", "height": 300, "width": 300}
        ],
        "product": "string",
        "type": "string",
        "uri": "string",
    }
