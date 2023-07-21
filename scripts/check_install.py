"""Check chopin is installed and has access to spotify."""
import sys

from chopin.managers.client import ClientManager
from chopin.managers.spotify_client import SpotifyClient
from chopin.schemas.track import TrackData
from chopin.schemas.user import UserData

if __name__ == "__main__":
    client = ClientManager(SpotifyClient(env_path=sys.argv[1]).get_client())
    try:
        user: UserData = client.get_current_user()
        tracks: list[TrackData] = client.get_history_tracks(time_range="short_term", limit=5)
        print(f"👋 Welcome {user.name}. Looks like everything is fine. Here is what you have been enjoying recently:")
        for track in tracks:
            print(f"\t{track.name} by {track.artists[0].name}")
    except Exception:
        print("😞 Looks like there have been an issue. Make sure you have followed the installation steps")
