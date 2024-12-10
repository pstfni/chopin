import random

from chopin.managers.track import shuffle_tracks


def test_shuffle_tracks(playlist_1_tracks):
    random.seed(42)
    tracks = shuffle_tracks(playlist_1_tracks)
    assert len(tracks) == len(playlist_1_tracks)
    assert tracks[0].name == "test_track_p_40"
