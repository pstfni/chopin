"""All the constants variables for Chopin."""


class ConstantsNamespace:
    """Namespace to hold and protect the constants."""

    @property
    def SPOTIFY_USER_URI(self):
        return "spotify:user:spotify"

    @property
    def SPOTIFY_API_HISTORY_LIMIT(self):
        return 50

    @property
    def SPOTIFY_RECOMMENDATION_SEED_LIMIT(self):
        return 5

    @property
    def MAX_RELATED_ARTISTS(self):
        return 10

    @property
    def MAX_TOP_TRACKS_ARTISTS(self):
        return 10

    @property
    def MAX_SEEDS(self):
        return 5

    @property
    def TRACK_FIELDS(self):
        return (
            "total, items.track.id, items.track.name, items.track.uri, items.track.duration_ms, items.track.popularity,"
            "items.track.album.uri, items.track.album.name, items.track.album.release_date, items.track.album.id,"
            "items.track.artists.uri, items.track.artists.name, items.track.artists.id, items.track.artists.genre"
        )


constants = ConstantsNamespace()
