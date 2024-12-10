"""Buttons related to the streamlit app."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from chopin.entrypoints.queue import queue


@dataclass
class Entrypoint:
    """Utility dataclass to describe an entrypoint in the app."""

    name: str
    docstring: str
    on_click: Callable | None = None
    args: dict[str, Any] | None = None


ENTRYPOINTS: list[Entrypoint] = [
    Entrypoint(name="queue", on_click=queue, docstring="Create a playlist from the user queue"),
]
