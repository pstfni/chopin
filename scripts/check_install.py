import sys
from typing import List

from icai.managers.client import ClientManager
from icai.managers.spotify_client import SpotifyClient
from icai.schemas.base import TrackData, UserData

if __name__ == "__main__":
    client = ClientManager(SpotifyClient(env_path=sys.argv[1]).get_client())
    try:
        user: UserData = client.get_current_user()
        tracks: List[TrackData] = client.get_history_tracks(time_range="short_term", limit=5)
        print(f"👋 Welcome {user.name}. Looks like everything is fine. Here is what you have been enjoying recently:")
        for track in tracks:
            print(f"\t{track.name} by {track.artists[0].name}")
    except Exception:
        print("😞 Looks like there have been an issue. Make sure you have followed the installation steps")
