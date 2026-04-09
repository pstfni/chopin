# AGENTS.md

## Project Overview

Chopin is a Spotify playlist manager CLI that lets users compose playlists from configured sources,
shuffle them, back up and restore playlists, convert the current queue to a playlist, and create
doppelganger playlists. An optional Streamlit web app is also available. As of November 2024,
Spotify removed 7 API routes, which significantly reduced the available feature set.

## Tech Stack

- Python >= 3.10
- Package manager: `uv`
- CLI framework: `click`
- Spotify API: `spotipy`
- Data validation and settings: `pydantic`, `pydantic_settings`
- YAML parsing: `ruamel.yaml`
- Linter/formatter: `ruff` (configured in `ruff.toml`)
- Test framework: `pytest`, `pytest-sugar`
- Optional web app: `streamlit`
- Docs: `mkdocs`, `mkdocstrings`, `mkdocs-material`

## Project Structure

```
chopin/
├── chopin/
│   ├── cli/          # Click-based CLI commands: compose, backup, restore, shuffle,
│   │                 #   from_queue, doppelganger, app (Streamlit launcher)
│   ├── client/       # Spotify API client wrapper (spotipy) and settings/configuration
│   ├── managers/     # Core business logic: playlist management, composition, track selection
│   ├── schemas/      # Pydantic models for playlists, tracks, artists, albums, users, compositions
│   ├── tools/        # Utility helpers: logging, dates, string/dict utilities
│   └── constants.py  # Application-wide constants
├── app/              # Optional Streamlit web interface
├── confs/            # YAML configuration files defining playlist composition sources
├── tests/            # Test suite mirroring the chopin/ package structure
├── docs/             # MkDocs documentation source
├── ruff.toml         # Ruff linter/formatter configuration
├── pyproject.toml    # Project metadata and dependencies
└── Makefile          # Developer convenience targets
```

## Development Setup

```bash
git clone git@github.com:pstfni/chopin.git
cd chopin/

# Full setup (downloads uv, installs deps, creates .env stub)
make setup

# Or, if uv is already installed
uv sync
```

Populate `.env` with your Spotify Developer credentials before running any command:

```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=...
```

Never commit `.env`.

## Build & Test Commands

```bash
# Run all tests
pytest

# Lint
ruff check .

# Format
ruff format .

# Verify installation and .env values
python scripts/check_install.py "./.env"
```

Pre-commit hooks run `ruff-check --fix`, `ruff-format`, and `docformatter` automatically on staged
files. Install them with `pre-commit install` after cloning.

## Coding Conventions

- Line length: 120 characters (enforced by ruff).
- Docstrings: Google style on all public functions, classes, and modules. `__init__.py` files and
  test files are exempt from docstring requirements.
- Imports: sorted and deduplicated by ruff (isort-compatible, rule set `I`).
- Do not use `*` imports. Prefer explicit named imports.
- Use `const` naming (`UPPER_SNAKE_CASE`) for module-level constants; add them to
  `chopin/constants.py` rather than scattering magic values throughout modules.
- Pydantic models live exclusively in `chopin/schemas/`. Do not define ad-hoc dataclasses or
  TypedDicts elsewhere when a schema is the right abstraction.
- CLI commands are thin wrappers. Business logic belongs in `chopin/managers/`, not in
  `chopin/cli/`.
- `chopin/tools/` is for stateless utility functions only. Do not add Spotify or manager logic
  there.
- Ruff rule sets in use: `F, E, W, I, N, D, UP, B, PERF, RUF`. Rules `N805` and `B008` are
  globally ignored.

## Architecture & Key Concepts

- **CLI entry point**: `chopin.cli:app` (defined in `chopin/cli/main.py`). Each sub-command is
  registered in that file. Add new commands there.
- **Client layer** (`chopin/client/`): wraps `spotipy` and exposes a typed interface to the rest
  of the application. Spotify credentials are loaded through `pydantic_settings` from the `.env`
  file.
- **Managers** (`chopin/managers/`): contain all orchestration logic (composition, playlist CRUD,
  track selection). Managers call the client; they do not call the CLI layer.
- **Schemas** (`chopin/schemas/`): Pydantic models representing Spotify domain objects. Models
  mirror the Spotify API response shapes and are the canonical data types passed between layers.
- **Composition configs** (`confs/*.yaml`): declarative YAML files that describe which playlists
  to draw from and how many tracks to select. The `compose` command consumes these files.

## Agent Behavioral Guidelines

- Always run `ruff check .` and `ruff format .` after modifying Python source files. Do not submit
  changes that produce ruff violations.
- Always run `pytest` after any logic change and confirm all tests pass.
- When adding a new CLI sub-command, register it in `chopin/cli/main.py` following the existing
  `app.add_command(...)` pattern.
- When adding a new Spotify API call, add it to `chopin/client/` — never call `spotipy` directly
  from managers or CLI modules.
- When adding a new domain concept, define its Pydantic schema in `chopin/schemas/` first, then
  build the manager logic around it.
- Do not add optional dependencies (e.g., `streamlit`) to the base `[project.dependencies]` in
  `pyproject.toml`. Use the existing `[project.optional-dependencies]` groups (`dev`, `docs`,
  `app`).
- Do not modify `.env` or commit secrets. If a new environment variable is required, document it
  in this file and in `chopin/client/settings.py`.
- When writing or updating tests, place them under `tests/` in a path that mirrors the source
  module (e.g., tests for `chopin/managers/playlist.py` go in `tests/managers/test_playlist.py`).

## Common Pitfalls & Gotchas

- **Spotify API limitations**: As of November 2024, Spotify removed 7 API endpoints. Before
  implementing a feature that depends on a specific Spotify API route, verify the route is still
  available in the current Spotify Web API documentation.
- **Authentication flow**: `spotipy` opens a browser redirect for the OAuth flow on first run.
  This requires a properly configured `SPOTIFY_REDIRECT_URI` in `.env` that matches the value
  registered in the Spotify Developer Dashboard.
- **ruamel.yaml vs PyYAML**: The project uses `ruamel.yaml`, not the standard `PyYAML`. Do not
  introduce `import yaml` (PyYAML); use `ruamel.yaml.YAML()` instead.
- **ruff ignores in tests**: `S`, `D`, and `N` rule groups are suppressed for all files under
  `tests/`. Do not suppress additional rule groups without a documented reason.
- **`__init__.py` F401**: Unused-import warnings (`F401`) are suppressed in all `__init__.py`
  files to allow deliberate re-exports. Use this only for intentional public API surface, not as
  a workaround for unneeded imports elsewhere.

## Out of Scope / Do Not Touch

- `.venv/` — managed entirely by `uv`. Never edit files inside this directory.
- `.env` — contains secrets. Never read, log, or commit its contents.
- `.git/` — never modify git internals directly.
