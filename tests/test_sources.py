from chopin.sources import Source, clear_registry, get_registry, get_sources, register


def test_get_registry_empty():
    clear_registry()
    assert get_registry() == {}


def test_get_registry():
    @register("playlists", str)
    def _dummy_function():
        pass

    registry = get_registry()
    assert "playlists" in registry
    assert isinstance(registry["playlists"], Source)
    assert registry["playlists"].key == "playlists"
    assert registry["playlists"].handler is _dummy_function
    assert registry["playlists"].pydantic_config_type is str

    # Test clear_registry while at it
    clear_registry()
    assert get_registry() == {}


def test_get_sources_empty():
    clear_registry()
    assert get_sources() == []


def test_get_sources():
    @register("uris", str)
    def _dummy_uri_func():
        pass

    @register("playlists", str)
    def _dummy_playlists_func():
        pass

    assert get_sources() == ["uris", "playlists"]
