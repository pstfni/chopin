"""Check chopin is installed and has access to spotify."""

from chopin.client.endpoints import get_current_user, get_top_tracks
from chopin.schemas.track import TrackData
from chopin.schemas.user import UserData

if __name__ == "__main__":
    try:
        user: UserData = get_current_user()
        tracks: list[TrackData] = get_top_tracks(time_range="short_term", limit=5)
        print(f"👋 Welcome {user.name}. Looks like everything is fine. Here is what you have been enjoying recently:")
        for track in tracks:
            print(f"\t{track.name} by {track.artists[0].name}")
    except Exception:
        print("😞 Looks like there have been an issue. Make sure you have followed the installation steps")
