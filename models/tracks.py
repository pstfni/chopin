from typing import Dict, List

import spotipy

from utils import get_logger, simplify_string, list_chunks
from schemas import PlaylistData, UserData, TrackData, TrackFeaturesData, ArtistData

logger = get_logger(__name__)


class Tracks:
    def __init__(self, spotify_client: spotipy.Spotify):
        self.client = spotify_client

    def get_tracks(self, track_ids: List[str], with_features: bool = False):
        retrieved_tracks: List[TrackData] = []
        for paginated_track_ids in list_chunks(track_ids, 50):
            tracks = self.client.tracks(paginated_track_ids)
            if with_features:
                tracks_features = self.client.audio_features(paginated_track_ids)
            retrieved_tracks.extend([TrackData.parse_obj(track) for track in tracks])

        return retrieved_tracks

    def get_user_playlists(self) -> List[PlaylistData]:
        playlists = self.client.current_user_playlists()['items']
        return [PlaylistData(name=simplify_string(p["name"]), uri=p["uri"]) for p in playlists]

    def get_current_user(self) -> UserData:
        return self.user

    def feed_mapping_values(self, mapping_value_dict: Dict[str, int]):
        self.value_mapping = mapping_value_dict
