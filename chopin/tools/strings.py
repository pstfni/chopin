"""Utilites to help deal with strings."""

import re
import unicodedata

import emoji


def simplify_string(text: str) -> str:
    """Simplify a string: lowercase, and no emojis."""
    text = emoji.replace_emoji(text)
    text = text.lower()
    text = text.rstrip(" ")
    text = text.lstrip(" ")
    text = text.replace("'", "")
    text = text.replace(" ", "")
    text = text.replace("&", "_")
    return text


def match_strings(strings: list[str]) -> bool:
    """Check if all strings match.

    They match if their lowercase, unicode stripped-off characters versions are similar.

    Args:
        strings: A list of strings to match

    Returns:
        True if all strings are the same (minus lowercase and unicode special character differences)
    """

    def _normalize_string(_string: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", _string.lower()) if unicodedata.category(c) != "Mn")

    if len(strings) < 2:
        return True
    target = _normalize_string(strings[0])
    return all([_normalize_string(s) == target for s in strings[1:]])


def extract_uri_from_playlist_link(playlist_link: str) -> str:
    """Parse a playlist link and returns the playlist URI. The playlist URI is later used to query the Spotify API.

    ??? example
        `https://open.spotify.com/playlist/37i9dQZF1DWWv8B5EWK7bn?si=8d52c3fef8d74064` becomes `37i9dQZF1DWWv8B5EWK7bn`

    Args:
        playlist_link: https link to a Spotify playlist.

    Returns:
        The playlist URI
    """
    pattern = r"playlist/([a-zA-Z0-9]+)\?"
    match = re.search(pattern, playlist_link)
    if match:
        return match.group(1)
    return ""
