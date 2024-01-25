"""Buttons related to the streamlit app."""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from chopin.entrypoints.new_releases import new_releases
from chopin.entrypoints.queue import queue
from chopin.entrypoints.recommend import recommend


@dataclass
class Entrypoint:
    name: str
    docstring: str  # todo: see if __doc__ or something is more suited ?
    on_click: Callable | None = None
    args: dict[str, Any] | None = None


ENTRYPOINTS: list[Entrypoint] = [
    Entrypoint(name="queue", on_click=queue, docstring="Create a playlist from the user queue"),
    Entrypoint(
        name="recommend",
        on_click=recommend,
        docstring="Create a playlist from available recommendations for the current user",
    ),
    Entrypoint(
        name="new releases",
        on_click=new_releases,
        args={"composition_config": "confs/recent.yaml"},
        docstring="Create a playlist from fresh releases.",
    ),
]
