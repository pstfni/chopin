"""Sources and registry for playlist composition."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass
class Source:
    """Dataclass for sources in the registry.

    Attributes:
        key: Source identifier
        handler: Decorated function
        pydantic_config_type: Configuration item.
    """

    key: str
    handler: Callable[..., list[T]]
    pydantic_config_type: type


_REGISTRY: dict[str, Source] = {}


def register(key: str, pydantic_config_type: type) -> Callable:
    """Decorator to add and register a composition source handler.

    Args:
        key: Source identifier, which should match the field name of the composer configuration.
            For example, `playlists` or `uris`.
        pydantic_config_type: The pydantic configuration item for the source.
            For example, `ComposerConfigItem`.

    Usage:
        ```py
        @register("playlists", ComposerConfigItem)
        def _add_from_playlists(items, release_range, added_at_range, **kwargs):
            ...
        ```
        This will update the registry with `add_from_playlists` when we are looking to populate the
        playlists source of the composer configuration.
    """

    def decorator(fn: Callable) -> Callable:
        _REGISTRY[key] = Source(key=key, handler=fn, pydantic_config_type=pydantic_config_type)
        return fn

    return decorator


def get_registry() -> dict[str, Source]:
    """Get current registry."""
    return _REGISTRY


def get_sources() -> list[str]:
    """Get currently registered sources.

    Registration order is preserved.
    """
    return list(_REGISTRY.keys())


def clear_registry() -> None:
    """Clear the registry."""
    _REGISTRY.clear()
    return None
