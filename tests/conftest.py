import pytest
from spotipy.client import Spotify

from chopin.managers.client import ClientManager
from chopin.schemas.artist import ArtistData
from chopin.schemas.playlist import PlaylistData
from chopin.schemas.track import TrackData, TrackFeaturesData


@pytest.fixture
def mock_client_manager():
    mock_client = Spotify()
    return ClientManager(mock_client)


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
        artists=[artist_data(id_)],
        features=TrackFeaturesData(
            acousticness=0.1,
            danceability=0.2,
            energy=0.3,
            instrumentalness=0.4,
            liveness=0.5,
            loudness=0.6,
            speechiness=0.7,
            valence=0.8,
            tempo=0.9,
            mode=1,
            key=2,
            analysis_url="url",
        ),
    )


def artist_data(id_: str = "id") -> ArtistData:
    """
    Helper to create artists.
    Args:
        id_: Argument to generate the id. Useful to make sure unique artists can be created across a test.

    Returns:
        An artist, schematized as an ArtistData
    """
    return ArtistData(name=f"test_artist_{id_}", id=f"{id_}", uri=f"spotify:artist:{id_}", genres=[])


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
def track_features_data():
    return TrackFeaturesData(
        acousticness=-1,
        danceability=-0.8,
        energy=-0.6,
        instrumentalness=-0.4,
        liveness=-0.2,
        loudness=0.0,
        speechiness=0.2,
        valence=0.4,
        tempo=0.6,
        mode=1,
        key=1,
        analysis_url="url",
    )


# Fixtures for values expected to be returned by the Spotify API.
# Taken straight from their documentation https://developer.spotify.com/documentation/web-api/reference
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


def spotify_track():
    return {
        "album": {
            "album_type": "compilation",
            "total_tracks": 9,
            "available_markets": ["CA", "BR", "IT"],
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "2up3OPMp9Tb4dAKM2erWXQ",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                    "height": 300,
                    "width": 300,
                }
            ],
            "name": "string",
            "release_date": "1981-12",
            "release_date_precision": "year",
            "restrictions": {"reason": "market"},
            "type": "album",
            "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
            "album_group": "compilation",
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "string",
                    "name": "string",
                    "type": "artist",
                    "uri": "string",
                }
            ],
        },
        "artists": [
            {
                "external_urls": {"spotify": "string"},
                "followers": {"href": "string", "total": 0},
                "genres": ["Prog rock", "Grunge"],
                "href": "string",
                "id": "string",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228\n",
                        "height": 300,
                        "width": 300,
                    }
                ],
                "name": "string",
                "popularity": 0,
                "type": "artist",
                "uri": "string",
            }
        ],
        "available_markets": ["string"],
        "disc_number": 0,
        "duration_ms": 0,
        "explicit": True,
        "external_ids": {"isrc": "string", "ean": "string", "upc": "string"},
        "external_urls": {"spotify": "string"},
        "href": "string",
        "id": "string",
        "is_playable": True,
        "restrictions": {"reason": "string"},
        "name": "string",
        "popularity": 0,
        "preview_url": "string",
        "track_number": 0,
        "type": "string",
        "uri": "string",
        "is_local": True,
    }
