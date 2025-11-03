"""Buttons related to the streamlit app."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from chopin.cli.compose import compose_from_new_releases
from chopin.cli.from_queue import from_queue


@dataclass
class Entrypoint:
    """Utility dataclass to describe an entrypoint in the app."""

    name: str
    docstring: str
    on_click: Callable | None = None
    args: dict[str, Any] | None = None


ENTRYPOINTS: list[Entrypoint] = [
    Entrypoint(name="queue", on_click=from_queue, docstring="Create a playlist from the user queue"),
    Entrypoint(
        name="new releases", on_click=compose_from_new_releases, docstring="Create a playlist from fresh releases"
    ),
]
