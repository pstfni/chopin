from typing import Any, Dict, List

import requests
import spotipy

from schemas.base import ArtistData, PlaylistData, TrackData, TrackFeaturesData, UserData
from utils import get_logger, simplify_string

logger = get_logger(__name__)

TRACK_FIELDS = (
    "total, items.track.id, items.track.name, items.track.uri, items.track.duration_ms, items.track.popularity,"
    "items.track.album.uri, items.track.album.name, items.track.album.release_date, items.track.album.id,"
    "items.track.artists.uri, items.track.artists.name, items.track.artists.id, items.track.artists.genre"
)
SPOTIFY_USER_URI = "spotify:user:spotify"


class ClientManager:
    """Custom class to handle all API calls to spotipy, the API lib with Spotify.

    All methods directly interacting with Spotify should be here.
    """

    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client
        self.user = None
        self._session = requests.Session()

    def create_playlist(self, name: str, description: str = "Randomly generated playlist"):
        if not self.user:
            self.user = self.get_current_user()
        playlist = self.client.user_playlist_create(user=self.user.id, name=name, description=description)
        return PlaylistData(name=playlist["name"], uri=playlist["uri"])

    def get_user_playlists(self) -> List[PlaylistData]:
        playlists = self.client.current_user_playlists().get("items", [])
        return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]

    def get_current_user(self) -> UserData:
        user = self.client.current_user()
        self.user = UserData(name=user["display_name"], id=user["id"], uri=user["uri"])
        return self.user

    def get_tracks(self, playlist_uri: str) -> List[TrackData]:
        """
        Get tracks of a given playlist
        Args:
            playlist_uri: The uri of the playlist

        Returns:
        A list of track uuids.
        """
        offset: int = 0
        tracks: List[TrackData] = []
        response: Dict[str, Any] = {"response": []}

        while response:
            response = self.client.playlist_items(
                playlist_uri,
                offset=offset,
                fields=TRACK_FIELDS,
                additional_types=["track"],
            )
            offset += len(response["items"])
            response_tracks = [TrackData.parse_obj(r["track"]) for r in response["items"]]
            tracks.extend(response_tracks)

            if len(response["items"]) == 0:
                break
        return tracks

    def get_tracks_audio_features(self, track_ids: List[str]) -> List[TrackFeaturesData]:
        audio_features: List[Dict[str, Any]] = []
        paginated_uris = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
        for page_uris in paginated_uris:
            audio_features.extend(self.client.audio_features(page_uris))
        return [TrackFeaturesData(**feature) for feature in audio_features]

    def add_tracks_to_playlist(self, playlist_uri: str, track_ids: List[str]):
        paginated_tracks = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
        for page_tracks in paginated_tracks:
            self.client.playlist_add_items(playlist_uri, page_tracks)

    def replace_tracks_in_playlist(self, playlist_uri: str, track_ids: List[str]):
        paginated_tracks = [track_ids[i : i + 99] for i in range(0, len(track_ids), 99)]
        for page_tracks in paginated_tracks:
            self.client.playlist_replace_items(playlist_uri, page_tracks)

    def get_hot_artists(self, limit=50) -> List[ArtistData]:
        response = self.client.current_user_top_artists(limit=limit, time_range="short_term")["items"]
        return [ArtistData(**artist) for artist in response]

    def get_hot_tracks(self, limit=50) -> List[TrackData]:
        response = self.client.current_user_top_tracks(limit=limit, time_range="short_term")["items"]
        return [TrackData(**track) for track in response]

    def get_top_artists(self, limit=50) -> List[ArtistData]:
        response = self.client.current_user_top_artists(limit=limit, time_range="long_term")["items"]
        return [ArtistData(**artist) for artist in response]

    def get_top_tracks(self, limit=50) -> List[TrackData]:
        response = self.client.current_user_top_tracks(limit=limit, time_range="long_term")["items"]
        return [TrackData(**track) for track in response]

    def get_queue(self) -> List[TrackData]:
        if not self.client.current_playback().get("is_playing"):
            raise ValueError(
                "Spotify should be active on a device and the playback should be on for the get_queue endpoint to work."
            )
        # unfortunately this has to be custom made ... Just a hack for now while waiting for spotipy implementation
        headers = {
            "Authorization": f"Bearer {self.client.auth_manager.get_access_token(as_dict=False)}",
            "Content-Type": "application/json",
        }
        route = "https://api.spotify.com/v1/me/player/queue"
        try:
            response = self._session.request(
                method="GET",
                url=route,
                headers=headers,
                timeout=5,
                proxies=None,
            )
            response.raise_for_status()
            results = response.json()
        except requests.exceptions.HTTPError as http_error:
            error_response = http_error.response
            raise spotipy.SpotifyException(
                error_response.status_code, -1, f"{route}\n{error_response}", headers=error_response.headers
            )
        except ValueError:
            results = None
        return [TrackData(**track) for track in results.get("queue")]

    def like_tracks(self, track_uris: List[str]):
        self.client.current_user_saved_tracks_add(track_uris)

    def get_likes(self) -> List[TrackData]:
        offset = 0
        tracks = []
        while True:
            response = self.client.current_user_saved_tracks(limit=20, offset=offset)
            tracks.extend(response.get("items"))
            offset += 20
            if not response.get("next"):
                break
        return [TrackData(**track["track"]) for track in tracks]

    def get_this_is_playlist(self, artist_name: str) -> PlaylistData | None:
        # NOTE : Strict match for 'This Is artist_name' !
        response = self.client.search(q=artist_name, limit=10, type="playlist")["playlists"]
        items = response.get("items")
        if not items:
            raise ValueError(f"Couldn't retrieve playlists for query {artist_name}")
        playlist = [
            playlist
            for playlist in items
            if playlist["owner"]["uri"] == SPOTIFY_USER_URI and playlist["name"].startswith(f"This Is {artist_name}")
        ]
        if playlist:
            return PlaylistData(**playlist[0])
        return

    def get_recommendations(
        self,
        seed_artists: List[str],
        seed_genres: List[str],
        seed_tracks: List[str],
        limit: int,
        **kwargs,
    ):
        return self.client.recommendations(seed_artists, seed_genres, seed_tracks, limit, **kwargs)
